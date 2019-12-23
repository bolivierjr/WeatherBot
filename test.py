###
# Copyright (c) 2018, Bruce Olivier
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

from peewee import SqliteDatabase, DatabaseError
from unittest import TestCase, mock
from supybot.test import PluginTestCase
from requests import RequestException, HTTPError
from .utils.errors import LocationNotFound
from .utils.helpers import lru_cache, ttl_cache
from .utils.helpers import find_geolocation, find_current_weather
from .test_responses import geo_response, failed_geo_response, weather_response
from .models.users import User, UserSchema


def _mock_error_response(
    status: int, raise_for_status: RequestException
) -> mock.Mock:
    mock_error = mock.Mock()
    mock_error.raise_for_status = mock.Mock()
    mock_error.raise_for_status.side_effect = raise_for_status
    mock_error.status_code = status

    return mock_error


class WeatherBotTestCase(PluginTestCase):
    plugins = ("WeatherBot",)


@mock.patch("requests.get", autospec=True)
class UtilsFindGeoTestCase(TestCase):
    geo_parameters = [
        "New York, NY",
        "70447",
        "Mandeville, LA",
        "70447",
        "New York, NY",
    ]

    def setUp(self) -> None:
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
class UtilsFindWeatherTestCase(TestCase):
    weather_parameters = [
        "37.8267,-122.4233",
        "40.714,-74.006",
        "37.8267,-122.4233",
    ]

    def setUp(self):
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


class UtilsErrorsTestCase(TestCase):
    def test_location_not_found_error(self) -> None:
        """
        Testing that LocationNotFound exception is a subclass of
        RequestException.
        """
        self.assertTrue(issubclass(LocationNotFound, RequestException))


# Sqlite3 test database
test_db = SqliteDatabase(":memory:")


class UserModelTestCase(TestCase):
    def setUp(self):
        test_db.connect()
        test_db.create_tables([User])
        User.create(
            nick="Johnno",
            host="test@test.com",
            location="New Orleans",
            region="Louisiana",
            coordinates="29.974,-90.087",
        )

    def tearDown(self):
        test_db.drop_tables([User])
        test_db.close()

    def test_user_model(self) -> None:
        test_user = User.get(User.nick == "Johnno")

        self.assertEqual(test_user.id, 1)
        self.assertEqual(test_user.nick, "Johnno")
        self.assertEqual(test_user.host, "test@test.com")
        self.assertEqual(test_user.location, "New Orleans")
        self.assertEqual(test_user.region, "Louisiana")
        self.assertEqual(test_user.coordinates, "29.974,-90.087")
        self.assertIsNotNone(test_user.created_at)

    def test_user_model_nick_unique(self) -> None:
        user = User(
            nick="Johnno",
            host="test@test.com",
            location="Covington",
            region="Louisiana",
            coordinates="29.974,-91.087",
        )

        with self.assertRaises(DatabaseError):
            user.save()
