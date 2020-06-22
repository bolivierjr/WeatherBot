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
from .utils.weather import WeatherAPI, DarkskyAPI
from .utils.services import WeatherService


# Sqlite3 test database
test_db = SqliteDatabase(":memory:")


def _mock_error_response(status: int, raise_for_status: RequestException) -> mock.Mock:
    mock_error = mock.Mock()
    mock_error.raise_for_status = mock.Mock()
    mock_error.raise_for_status.side_effect = raise_for_status
    mock_error.status_code = status

    return mock_error


class MockAPI(WeatherAPI):
    """
    Mock WeatherAPI class to inject into WeatherService for testing.
    """

    def __init__(self, query):
        self.query = query
        self.location = None
        self.region = None
        self.coordinates = None

    def find_current_weather(self):
        return weather_response

    def find_geolocation(self):
        self.location = "New York"
        self.region = "NY"
        self.coordinates = "40.714,-74.006"

    def display_format(self, format):
        return display_default_response


####################################
# Unit tests for plugin.py commands
####################################
class WeatherBotTestCase(PluginTestCase):
    plugins = ("WeatherBot",)


##################################
# Unit tests for utils/services.py
##################################
class UtilsWeatherServiceTestCase(SupyTestCase):
    def test_get_current(self):
        """
        Testing get_current is returning the correct string response
        to send back to the user.
        """
        mock_api = MockAPI("New York, NY")
        service = WeatherService(mock_api)
        weather = service.get_current(format=1)
        self.assertEqual(weather, display_default_response)
        self.assertTrue(isinstance(mock_api, WeatherAPI))

    def test_get_location(self):
        """
        Testing get_location is returning the correct dictonary of location values.
        """
        expected = {"location": "New York", "region": "NY", "coordinates": "40.714,-74.006"}
        service = WeatherService(MockAPI("New York, NY"))
        location = service.get_location()
        self.assertEqual(location, expected)


##################################
# Unit tests for utils/weather.py
##################################
class UtilsDarkskyApiTestCase(SupyTestCase):
    def test_darkskyapi_implements_weatherapi(self):
        """
        Testing DarkskyAPI implements from the WeatherAPI interface.
        """
        weather = DarkskyAPI("New York, New York")
        self.assertTrue(isinstance(weather, WeatherAPI))


@mock.patch("requests.get", autospec=True)
class UtilsFindGeoTestCase(SupyTestCase):
    def setUp(self) -> None:
        SupyTestCase.setUp(self)

    def test_find_geolocation(self, mocker: mock.patch) -> None:
        """
        Testing find_geolocation is returning the correct dictionary of results back.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = geo_response
        service = DarkskyAPI("New York, NY")
        service.find_geolocation()

        expected = {
            "location": "New York",
            "region": "New York",
            "coordinates": "40.714,-74.006",
        }
        self.assertEqual(service.location, expected["location"])
        self.assertEqual(service.region, expected["region"])
        self.assertEqual(service.coordinates, expected["coordinates"])

    def test_find_geolocation_raises_location_not_found(self, mocker: mock.patch) -> None:
        """
        Testing find_geolocation raises a LocationNotFound exception
        when the geolocation api is unable to find location given.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = failed_geo_response

        service = DarkskyAPI("70888")
        self.assertRaises(LocationNotFound, service.find_geolocation)

    def test_find_geolocation_raises_http_error(self, mocker: mock.patch) -> None:
        """
        Testing that find_geolocation raises an HTTPError when a
        failed http response occurs.
        """
        mocked_error = _mock_error_response(status=404, raise_for_status=HTTPError("FAILED"))
        mocker.return_value = mocked_error

        service = DarkskyAPI("70447")
        self.assertRaises(HTTPError, service.find_geolocation)
        self.assertTrue(mocker.return_value.raise_for_status.called)


@mock.patch("requests.get", autospec=True)
class UtilsFindWeatherTestCase(SupyTestCase):
    def setUp(self):
        SupyTestCase.setUp(self)
        self.side_effects = [
            mock.Mock(status_code=200, json=lambda: geo_response),
            mock.Mock(status_code=200, json=lambda: weather_response),
        ]

    def test_find_current_weather(self, mocker: mock.patch) -> None:
        """
        Testing find_current_weather is returning the correct dictionary of results back.
        """
        mocker.side_effect = self.side_effects
        service = DarkskyAPI("40.714,-74.006")
        service.find_current_weather()

        self.assertEqual(service.data, weather_response)

    def test_find_geolocation_raises_http_error(self, mocker: mock.patch) -> None:
        """
        Testing that find_current_weather raises an HTTPError
        when a failed http response occurs.
        """
        mocked_error = _mock_error_response(status=404, raise_for_status=HTTPError("FAILED"))
        mocker.return_value = mocked_error

        service = DarkskyAPI("37.8267,-122.4233")
        self.assertRaises(HTTPError, service.find_current_weather)
        self.assertTrue(mocker.return_value.raise_for_status.called)


@mock.patch("requests.get", autospec=True)
class UtilsDisplayFormatTestCase(SupyTestCase):
    def test_default_display_format(self, mocker):
        """
        Testing that display_format() returns back the
        proper format F/C by default.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = geo_response

        service = DarkskyAPI("New York, New York")
        service.find_geolocation()
        service.data = weather_response
        display_fc_default = service.display_format()

        self.assertEqual(display_fc_default, display_default_response)

    def test_cf_display_format(self, mocker):
        """
        Testing that display_format() returns back the
        proper format when user wants C/F metric first.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = geo_response

        service = DarkskyAPI("New York, New York")
        service.find_geolocation()
        service.data = weather_response
        display_cf = service.display_format(format=2)

        self.assertEqual(display_cf, display_cf_response)


class UtilsFormatDirectionTestCase(SupyTestCase):
    def test_format_directions(self):
        """
        Test that format_directions() returns back
        the proper cardinal direction given the degrees.
        """
        service = DarkskyAPI("New York, New York")
        self.assertEqual(service.format_directions(300), "WNW")

    def test_format_directions_with_none(self):
        """
        Test that format_directions() returns back
        "N/A if None is given for the parameter.
        """
        service = DarkskyAPI("New York, New York")
        self.assertEqual(service.format_directions(None), "N/A")


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


class UserModelCheckUserTestCase(SupyTestCase):
    def tearDown(self):
        User.drop_table()
        test_db.close()
        SupyTestCase.tearDown(self)

    def test_check_user_raises_exceptions(self):
        """
        Testing that check_users() method raises
        DatabaseError when there is no sqlite db file
        or no user table created yet.
        """
        self.assertRaises(DatabaseError, User.check_user, "Johnno")

        with self.assertRaises(DatabaseError):
            User.create_table()
            User.drop_table()
            User.check_user("Johnno")

    def test_check_user(self):
        """
        Testing that check_users() method returns
        back an instance of User model or None if
        no user is found.
        """
        User.create_table()
        User.create(
            nick="Johnno",
            host="test@test.com",
            location="New Orleans",
            region="Louisiana",
            coordinates="29.974,-90.087",
            format=1,
        )

        self.assertTrue(isinstance(User.check_user("Johnno"), User))
        self.assertEqual(User.check_user("Bruce"), None)


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
            self.assertEqual(exc.messages, {"location": ["location is too long."]})

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
                exc.messages, {"format": ["Format setting must be set to 1 for imperial or 2 for metric units first."]},
            )
