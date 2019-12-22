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

from unittest import TestCase, mock
from supybot.test import *
from .utils.helpers import find_geolocation
from .utils.errors import LocationNotFound


class WeatherBotTestCase(PluginTestCase):
    plugins = ("WeatherBot",)


class UtilsHelpersTestCase(TestCase):
    geo_response = {
        "location": {
            "name": "New York",
            "country": "United States of America",
            "region": "New York",
            "lat": "40.714",
            "lon": "-74.006",
            "timezone_id": "America/New_York",
            "localtime": "2019-12-21 17:28",
            "localtime_epoch": 1576949280,
            "utc_offset": "-5.0",
        }
    }
    failed_geo_response = {
        "success": False,
        "error": {
            "code": 615,
            "type": "request_failed",
            "info": "Your API request failed. Please try again or contact support.",
        },
    }
    geo_parameters = [
        "New York, NY",
        "70447",
        "Mandeville, LA",
        "70447",
        "New York, NY",
    ]

    @mock.patch("requests.get", autospec=True)
    def test_find_geolocation_and_lru_cache(self, mocker):
        """
        Testing lru_cache is only making requests hit the geolocation
        api on new results that aren't cached and find_geolocation
        is returning the correct dictionary of results back.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = self.geo_response
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

    @mock.patch("requests.get", autospec=True)
    def test_find_geolocation_raises_exception(self, mocker):
        """
        Testing find_geolocation raises a LocationNotFound exception
        when the geolocation api is unable to find location given.
        """
        mocker.return_value.status_code = 200
        mocker.return_value.json.return_value = self.failed_geo_response

        self.assertRaises(LocationNotFound, find_geolocation, "70888")
