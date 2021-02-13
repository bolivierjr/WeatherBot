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

geo_response_without_region = {"location": {**geo_response["location"], "region": " ", "country": "USA"}}

failed_geo_response = {
    "success": False,
    "error": {
        "code": 615,
        "type": "request_failed",
        "info": "Your API request failed. Please try again or contact support.",  # noqa: E501
    },
}

weather_response = {
    "lat": 37.8267,
    "lon": -122.4233,
    "timezone": "America/New York",
    "timezone_offset": -21600,
    "current": {
        "dt": 1577043254,
        "sunrise": 1608124431,
        "sunset": 1608160224,
        "icon": "rain",
        "temp": 52.61,
        "feels_like": 52.61,
        "dew_point": 47.21,
        "humidity": 82,
        "pressure": 1008.8,
        "wind_speed": 12.81,
        "wind_deg": 300,
        "clouds": 0.8,
        "uvi": 1,
        "visibility": 10,
        "weather": [{"id": 701, "main": "light Rain", "description": "light rain", "icon": "50n"}],
    },
    "daily": [
        {
            "dt": 1577001600,
            "icon": "rain",
            "sunrise": 1577028180,
            "sunset": 1577062560,
            "temp": {"day": 50.31, "max": 54.3, "min": 42.65},
            "feels-like": {"day": 50.31, "max": 54.3, "min": 42.65},
            "dew_point": 45.03,
            "humidity": 76,
            "pressure": 1008.9,
            "wind_speed": 10.32,
            "wind_deg": 212,
            "clouds": 0.56,
            "uvi": 2,
            "weather": [
                {
                    "id": 803,
                    "main": "light rain in the morning and afternoon",
                    "description": "light rain in the morning and afternoon",
                    "icon": "rain",
                }
            ],
        }
    ],
}

display_default_response = (
    f"\x02New York, New York\x02 :: Light Rain 52.6F/11.4C (Humidity: 82%) | "
    f"\x02Feels like\x02: 52.6F/11.4C | \x02Wind\x02: WNW at 12.8mph/20.6kph | "  # noqa: E501
    f"\x02Today\x02: Light rain in the morning and afternoon. High 54.3F/12.4C"
    f" - Low 42.6F/5.9C"
)

display_cf_response = (
    f"\x02New York, New York\x02 :: Light Rain 11.4C/52.6F (Humidity: 82%) | "
    f"\x02Feels like\x02: 11.4C/52.6F | \x02Wind\x02: WNW at 20.6kph/12.8mph | "  # noqa: E501
    f"\x02Today\x02: Light rain in the morning and afternoon. High 12.4C/54.3F"
    f" - Low 5.9C/42.6F"
)
