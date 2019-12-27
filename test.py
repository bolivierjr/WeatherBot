###
# Copyright (c) 2019, Bruce Olivier
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from unittest import mock
from marshmallow import ValidationError
from peewee import SqliteDatabase, DatabaseError
from supybot.test import PluginTestCase, SupyTestCase
from requests import RequestException, HTTPError
from .models.users import User, UserSchema
from .utils.errors import LocationNotFound, WeatherNotFound
from .test_responses import (
    geo_response,
    failed_geo_response,
    weather_response,
    display_default_response,
    display_cf_response,
)
from .utils.helpers import (
    find_geolocation,
    find_current_weather,
    display_format,
    format_directions,
    ttl_cache,
    lru_cache,
)


def _mock_error_response(
    status: int, raise_for_status: RequestException
) -> mock.Mock:
    mock_error = mock.Mock()
    mock_error.raise_for_status = mock.Mock()
    mock_error.raise_for_status.side_effect = raise_for_status
    mock_error.status_code = status

    return mock_error


####################################
# Unit tests for plugin.py commands
####################################
class WeatherBotTestCase(PluginTestCase):
    plugins = ("WeatherBot",)


##################################
# Unit tests for utils/helpers.py
##################################
@mock.patch("requests.get", autospec=True)
class UtilsFindGeoTestCase(SupyTestCase):
    geo_parameters = [
        "New York, NY",
        "70447",
        "Mandeville, LA",
        "70447",
        "New York, NY",
    ]

    def setUp(self) -> None:
        SupyTestCase.setUp(self)
        lru_cache.clear()  # Clear any cached results

    def test_find_geolocation_and_lru_cache(self, mocker: mock.patch) -> None:
        """
        Testing lru_cache is only making requests hit the geolocation
        api on new results that aren't cached and find_geolocation
        is returning the correct dictionary of results back.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = geo_response
        for param in self.geo_parameters:
            geolocation = find_geolocation(param)

        expected = {
            "location": "New York",
            "region": "New York",
            "coordinates": "40.714,-74.006",
        }
        self.assertEqual(mocker.call_count, 3)
        self.assertEqual(geolocation, expected)
        self.assertTrue(mocker.return_value.raise_for_status.called)

    def test_find_geolocation_raises_location_not_found(
        self, mocker: mock.patch
    ) -> None:
        """
        Testing find_geolocation raises a LocationNotFound exception
        when the geolocation api is unable to find location given.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = failed_geo_response

        self.assertRaises(LocationNotFound, find_geolocation, "70888")

    def test_find_geolocation_raises_http_error(
        self, mocker: mock.patch
    ) -> None:
        """
        Testing that find_geolocation raises an HTTPError when a
        failed http response occurs.
        """
        mocked_error = _mock_error_response(
            status=404, raise_for_status=HTTPError("FAILED")
        )
        mocker.return_value = mocked_error

        self.assertRaises(HTTPError, find_geolocation, "70447")


@mock.patch("requests.get", autospec=True)
class UtilsFindWeatherTestCase(SupyTestCase):
    weather_parameters = [
        "37.8267,-122.4233",
        "40.714,-74.006",
        "37.8267,-122.4233",
    ]

    def setUp(self):
        SupyTestCase.setUp(self)
        ttl_cache.clear()  # Clear any cached results

    def test_find_current_weather_and_ttl_cache(
        self, mocker: mock.patch
    ) -> None:
        """
        Testing ttl_cache is only making requests hit the weather
        api on new results that aren't cached and find_current_weather
        is returning the correct dictionary of results back.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = weather_response
        for param in self.weather_parameters:
            weather = find_current_weather(param)

        self.assertEqual(mocker.call_count, 2)
        self.assertEqual(weather, weather_response)
        self.assertTrue(mocker.return_value.raise_for_status.called)

    def test_find_geolocation_raises_http_error(
        self, mocker: mock.patch
    ) -> None:
        """
        Testing that find_current_weather raises an HTTPError
        when a failed http response occurs.
        """
        mocked_error = _mock_error_response(
            status=404, raise_for_status=HTTPError("FAILED")
        )
        mocker.return_value = mocked_error

        self.assertRaises(HTTPError, find_current_weather, "37.8267,-122.4233")


class UtilsDisplayFormatTestCase(SupyTestCase):
    def test_default_display_format(self):
        """
        Testing that display_format() returns back the
        proper format F/C by default.
        """
        display_fc_default = display_format(
            "New York", "New York", weather_response
        )

        self.assertEqual(display_fc_default, display_default_response)

    def test_cf_display_format(self):
        """
        Testing that display_format() returns back the
        proper format when user wants C/F metric first.
        """
        display_cf = display_format(
            "New York", "New York", weather_response, format=2
        )

        self.assertEqual(display_cf, display_cf_response)


class UtilsFormatDirectionTestCase(SupyTestCase):
    def test_format_directions(self):
        """
        Test that format_directions() returns back
        the proper cardinal direction given the degrees.
        """
        self.assertEqual(format_directions(300), "WNW")

    def test_format_directions_with_none(self):
        """
        Test that format_directions() returns back
        "N/A if None is given for the parameter.
        """
        self.assertEqual(format_directions(None), "N/A")


#################################
# Unit tests for utils/errors.py
#################################
class UtilsErrorsTestCase(SupyTestCase):
    def test_location_not_found_error(self) -> None:
        """
        Testing that LocationNotFound exception is a subclass of
        RequestException.
        """
        self.assertTrue(issubclass(LocationNotFound, RequestException))

    def test_weather_not_found_error(self) -> None:
        """
        Testing that WeatherNotFound exception is a subclass of
        RequestException.
        """
        self.assertTrue(issubclass(WeatherNotFound, RequestException))


#################################
# Unit tests for models/users.py
#################################

# Sqlite3 test database
test_db = SqliteDatabase(":memory:")


class UserModelTestCase(SupyTestCase):
    def setUp(self):
        SupyTestCase.setUp(self)
        User.drop_table()
        User.create_table()
        User.create(
            nick="Johnno",
            host="test@test.com",
            location="New Orleans",
            region="Louisiana",
            coordinates="29.974,-90.087",
            format=1,
        )

    def tearDown(self):
        User.drop_table()
        test_db.close()
        SupyTestCase.tearDown(self)

    def test_user_model(self) -> None:
        """
        Test the user model created gives back the
        proper attributes that was fed to the database
        and saved.
        """
        test_user = User.get(User.nick == "Johnno")

        self.assertEqual(test_user.id, 1)
        self.assertEqual(test_user.nick, "Johnno")
        self.assertEqual(test_user.host, "test@test.com")
        self.assertEqual(test_user.location, "New Orleans")
        self.assertEqual(test_user.region, "Louisiana")
        self.assertEqual(test_user.coordinates, "29.974,-90.087")
        self.assertEqual(test_user.format, 1)
        self.assertIsNotNone(test_user.created_at)
        self.assertEqual(repr(test_user), "<User Johnno>")

    def test_user_model_nick_unique(self) -> None:
        """
        Test that a DatabaseError is raised if the unique
        user is tying to be saved again to the database.
        """
        user = User(
            nick="Johnno",
            host="test@test.com",
            location="Covington",
            region="Louisiana",
            coordinates="29.974,-91.087",
            format=1,
        )

        with self.assertRaises(DatabaseError):
            user.save()


class UserModelCreateTables(SupyTestCase):
    def tearDown(self):
        User.drop_table()
        test_db.close()
        SupyTestCase.tearDown(self)

    def test_create_table(self):
        """
        Test the custom create_tables() class method in the User model.
        """
        self.assertEqual(User.create_tables(), "Created users table.")
        self.assertEqual(User.create_tables(), "Users table already created.")
        self.assertTrue(User.table_exists())


class UserSchemaTestCase(SupyTestCase):
    def test_user_schema(self):
        """
        Tests the UserSchema returns back a dictionary and
        fails no validations with everything required.
        """
        user_info = {
            "nick": "Johnno",
            "host": "test@test.com",
            "location": "Covington",
            "region": "Louisiana",
            "coordinates": "29.974,-91.087",
            "format": 1,
        }
        user_schema = UserSchema().load(user_info)

        self.assertEqual(user_schema, user_info)

    def test_user_schema_raises_location_validation(self):
        """
        Tests the custom validation and error messages made for
        the location element in UserSchema.
        """
        with self.assertRaises(ValidationError):
            UserSchema().load({"location": 81 * "7"}, partial=True)

        try:
            UserSchema().load({"location": 81 * "7"}, partial=True)
        except ValidationError as exc:
            self.assertEqual(
                exc.messages, {"location": ["location is too long."]}
            )

    def test_user_schema_raises_format_validation(self):
        """
        Tests the custom validation and error messages made for
        the format element in UserSchema.
        """
        with self.assertRaises(ValidationError):
            UserSchema().load({"format": 3}, partial=True)

        with self.assertRaises(ValidationError):
            UserSchema().load({"format": 0}, partial=True)

        try:
            UserSchema().load({"format": 3}, partial=True)
        except ValidationError as exc:
            self.assertEqual(
                exc.messages,
                {
                    "format": [
                        "Format setting must be set to 1 for imperial or 2 for "
                        "metric units first."
                    ]
                },
            )
