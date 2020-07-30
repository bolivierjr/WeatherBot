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

geo_response_without_region = {"location": {**geo_response["location"], "region": "", "country": "USA"}}

failed_geo_response = {
    "success": False,
    "error": {
        "code": 615,
        "type": "request_failed",
        "info": "Your API request failed. Please try again or contact support.",  # noqa: E501
    },
}

weather_response = {
    "latitude": 37.8267,
    "longitude": -122.4233,
    "timezone": "America/Los_Angeles",
    "currently": {
        "time": 1577043254,
        "summary": "Light Rain",
        "icon": "rain",
        "nearestStormDistance": 0,
        "precipIntensity": 0.03,
        "precipIntensityError": 0.015,
        "precipProbability": 1,
        "precipType": "rain",
        "temperature": 52.61,
        "apparentTemperature": 52.61,
        "dewPoint": 47.21,
        "humidity": 0.82,
        "pressure": 1008.8,
        "windSpeed": 12.81,
        "windGust": 16.54,
        "windBearing": 300,
        "cloudCover": 0.8,
        "uvIndex": 1,
        "visibility": 10,
        "ozone": 342.1,
    },
    "daily": {
        "summary": "Light rain throughout the week.",
        "icon": "rain",
        "data": [
            {
                "time": 1577001600,
                "summary": "Light rain in the morning and afternoon.",
                "icon": "rain",
                "sunriseTime": 1577028180,
                "sunsetTime": 1577062560,
                "moonPhase": 0.89,
                "precipIntensity": 0.0133,
                "precipIntensityMax": 0.0749,
                "precipIntensityMaxTime": 1577026800,
                "precipProbability": 0.94,
                "precipType": "rain",
                "temperatureHigh": 54.3,
                "temperatureHighTime": 1577035980,
                "temperatureLow": 42.65,
                "temperatureLowTime": 1577114280,
                "apparentTemperatureHigh": 53.8,
                "apparentTemperatureHighTime": 1577035980,
                "apparentTemperatureLow": 39.19,
                "apparentTemperatureLowTime": 1577112600,
                "dewPoint": 45.03,
                "humidity": 0.76,
                "pressure": 1008.9,
                "windSpeed": 10.32,
                "windGust": 25.58,
                "windGustTime": 1577009280,
                "windBearing": 212,
                "cloudCover": 0.56,
                "uvIndex": 2,
                "uvIndexTime": 1577045640,
                "visibility": 9.935,
                "ozone": 335.1,
                "temperatureMin": 48.55,
                "temperatureMinTime": 1577088000,
                "temperatureMax": 55.34,
                "temperatureMaxTime": 1577014560,
                "apparentTemperatureMin": 46.41,
                "apparentTemperatureMinTime": 1577088000,
                "apparentTemperatureMax": 54.84,
                "apparentTemperatureMaxTime": 1577014560,
            },
            {
                "time": 1577088000,
                "summary": "Clear throughout the day.",
                "icon": "clear-day",
                "sunriseTime": 1577114640,
                "sunsetTime": 1577148960,
                "moonPhase": 0.93,
                "precipIntensity": 0.0001,
                "precipIntensityMax": 0.0002,
                "precipIntensityMaxTime": 1577167740,
                "precipProbability": 0.14,
                "precipType": "rain",
                "temperatureHigh": 53.8,
                "temperatureHighTime": 1577144040,
                "temperatureLow": 45.57,
                "temperatureLowTime": 1577199300,
                "apparentTemperatureHigh": 53.3,
                "apparentTemperatureHighTime": 1577144040,
                "apparentTemperatureLow": 44.14,
                "apparentTemperatureLowTime": 1577198820,
                "dewPoint": 40.42,
                "humidity": 0.74,
                "pressure": 1012.6,
                "windSpeed": 5.8,
                "windGust": 12.5,
                "windGustTime": 1577113740,
                "windBearing": 330,
                "cloudCover": 0.25,
                "uvIndex": 2,
                "uvIndexTime": 1577131620,
                "visibility": 10,
                "ozone": 343.6,
                "temperatureMin": 42.65,
                "temperatureMinTime": 1577114280,
                "temperatureMax": 53.8,
                "temperatureMaxTime": 1577144040,
                "apparentTemperatureMin": 39.19,
                "apparentTemperatureMinTime": 1577112600,
                "apparentTemperatureMax": 53.3,
                "apparentTemperatureMaxTime": 1577144040,
            },
            {
                "time": 1577174400,
                "summary": "Light rain in the evening and overnight.",
                "icon": "rain",
                "sunriseTime": 1577201040,
                "sunsetTime": 1577235420,
                "moonPhase": 0.97,
                "precipIntensity": 0.0019,
                "precipIntensityMax": 0.0142,
                "precipIntensityMaxTime": 1577260800,
                "precipProbability": 0.55,
                "precipType": "rain",
                "temperatureHigh": 52.12,
                "temperatureHighTime": 1577224800,
                "temperatureLow": 48.02,
                "temperatureLowTime": 1577288640,
                "apparentTemperatureHigh": 51.62,
                "apparentTemperatureHighTime": 1577224800,
                "apparentTemperatureLow": 45.86,
                "apparentTemperatureLowTime": 1577266680,
                "dewPoint": 41.55,
                "humidity": 0.75,
                "pressure": 1013.6,
                "windSpeed": 5.3,
                "windGust": 12.7,
                "windGustTime": 1577221380,
                "windBearing": 250,
                "cloudCover": 0.76,
                "uvIndex": 2,
                "uvIndexTime": 1577217720,
                "visibility": 10,
                "ozone": 346.7,
                "temperatureMin": 45.57,
                "temperatureMinTime": 1577199300,
                "temperatureMax": 52.12,
                "temperatureMaxTime": 1577224800,
                "apparentTemperatureMin": 44.14,
                "apparentTemperatureMinTime": 1577198820,
                "apparentTemperatureMax": 51.62,
                "apparentTemperatureMaxTime": 1577224800,
            },
            {
                "time": 1577260800,
                "summary": "Light rain in the morning.",
                "icon": "rain",
                "sunriseTime": 1577287500,
                "sunsetTime": 1577321820,
                "moonPhase": 1,
                "precipIntensity": 0.0094,
                "precipIntensityMax": 0.0434,
                "precipIntensityMaxTime": 1577276100,
                "precipProbability": 0.78,
                "precipType": "rain",
                "temperatureHigh": 52.17,
                "temperatureHighTime": 1577311920,
                "temperatureLow": 42.34,
                "temperatureLowTime": 1577370780,
                "apparentTemperatureHigh": 51.67,
                "apparentTemperatureHighTime": 1577311920,
                "apparentTemperatureLow": 40.81,
                "apparentTemperatureLowTime": 1577340300,
                "dewPoint": 42.15,
                "humidity": 0.77,
                "pressure": 1011.7,
                "windSpeed": 8.36,
                "windGust": 21.99,
                "windGustTime": 1577328240,
                "windBearing": 83,
                "cloudCover": 0.82,
                "uvIndex": 1,
                "uvIndexTime": 1577304360,
                "visibility": 10,
                "ozone": 389.3,
                "temperatureMin": 44.97,
                "temperatureMinTime": 1577344500,
                "temperatureMax": 52.17,
                "temperatureMaxTime": 1577311920,
                "apparentTemperatureMin": 40.81,
                "apparentTemperatureMinTime": 1577340300,
                "apparentTemperatureMax": 51.67,
                "apparentTemperatureMaxTime": 1577311920,
            },
            {
                "time": 1577347200,
                "summary": "Clear throughout the day.",
                "icon": "clear-day",
                "sunriseTime": 1577373900,
                "sunsetTime": 1577408280,
                "moonPhase": 0.03,
                "precipIntensity": 0.0001,
                "precipIntensityMax": 0.0002,
                "precipIntensityMaxTime": 1577372400,
                "precipProbability": 0.05,
                "precipType": "rain",
                "temperatureHigh": 54.76,
                "temperatureHighTime": 1577403060,
                "temperatureLow": 43.25,
                "temperatureLowTime": 1577459220,
                "apparentTemperatureHigh": 54.26,
                "apparentTemperatureHighTime": 1577403060,
                "apparentTemperatureLow": 41.67,
                "apparentTemperatureLowTime": 1577459340,
                "dewPoint": 36.23,
                "humidity": 0.65,
                "pressure": 1015.1,
                "windSpeed": 4.3,
                "windGust": 12.48,
                "windGustTime": 1577393820,
                "windBearing": 4,
                "cloudCover": 0,
                "uvIndex": 2,
                "uvIndexTime": 1577391060,
                "visibility": 10,
                "ozone": 361.9,
                "temperatureMin": 42.34,
                "temperatureMinTime": 1577370780,
                "temperatureMax": 54.76,
                "temperatureMaxTime": 1577403060,
                "apparentTemperatureMin": 40.91,
                "apparentTemperatureMinTime": 1577371080,
                "apparentTemperatureMax": 54.26,
                "apparentTemperatureMaxTime": 1577403060,
            },
            {
                "time": 1577433600,
                "summary": "Clear throughout the day.",
                "icon": "clear-day",
                "sunriseTime": 1577460300,
                "sunsetTime": 1577494740,
                "moonPhase": 0.07,
                "precipIntensity": 0,
                "precipIntensityMax": 0.0003,
                "precipIntensityMaxTime": 1577437200,
                "precipProbability": 0.01,
                "temperatureHigh": 55.17,
                "temperatureHighTime": 1577489460,
                "temperatureLow": 42.08,
                "temperatureLowTime": 1577545560,
                "apparentTemperatureHigh": 54.67,
                "apparentTemperatureHighTime": 1577489460,
                "apparentTemperatureLow": 37.67,
                "apparentTemperatureLowTime": 1577545800,
                "dewPoint": 35.55,
                "humidity": 0.61,
                "pressure": 1020.2,
                "windSpeed": 4.11,
                "windGust": 8.97,
                "windGustTime": 1577473800,
                "windBearing": 31,
                "cloudCover": 0.09,
                "uvIndex": 2,
                "uvIndexTime": 1577477400,
                "visibility": 10,
                "ozone": 337.6,
                "temperatureMin": 43.25,
                "temperatureMinTime": 1577459220,
                "temperatureMax": 55.17,
                "temperatureMaxTime": 1577489460,
                "apparentTemperatureMin": 41.67,
                "apparentTemperatureMinTime": 1577459340,
                "apparentTemperatureMax": 54.67,
                "apparentTemperatureMaxTime": 1577489460,
            },
            {
                "time": 1577520000,
                "summary": "Mostly cloudy throughout the day.",
                "icon": "partly-cloudy-day",
                "sunriseTime": 1577546760,
                "sunsetTime": 1577581140,
                "moonPhase": 0.1,
                "precipIntensity": 0,
                "precipIntensityMax": 0.0003,
                "precipIntensityMaxTime": 1577535060,
                "precipProbability": 0.02,
                "temperatureHigh": 52.53,
                "temperatureHighTime": 1577575980,
                "temperatureLow": 42.85,
                "temperatureLowTime": 1577631300,
                "apparentTemperatureHigh": 52.03,
                "apparentTemperatureHighTime": 1577575980,
                "apparentTemperatureLow": 40.16,
                "apparentTemperatureLowTime": 1577630760,
                "dewPoint": 34.91,
                "humidity": 0.64,
                "pressure": 1023.6,
                "windSpeed": 5.91,
                "windGust": 10.63,
                "windGustTime": 1577546700,
                "windBearing": 50,
                "cloudCover": 0.54,
                "uvIndex": 2,
                "uvIndexTime": 1577563380,
                "visibility": 10,
                "ozone": 309.5,
                "temperatureMin": 42.08,
                "temperatureMinTime": 1577545560,
                "temperatureMax": 52.53,
                "temperatureMaxTime": 1577575980,
                "apparentTemperatureMin": 37.67,
                "apparentTemperatureMinTime": 1577545800,
                "apparentTemperatureMax": 52.03,
                "apparentTemperatureMaxTime": 1577575980,
            },
            {
                "time": 1577606400,
                "summary": "Possible light rain overnight.",
                "icon": "rain",
                "sunriseTime": 1577633160,
                "sunsetTime": 1577667600,
                "moonPhase": 0.13,
                "precipIntensity": 0.0041,
                "precipIntensityMax": 0.0366,
                "precipIntensityMaxTime": 1577685420,
                "precipProbability": 0.41,
                "precipType": "rain",
                "temperatureHigh": 52.84,
                "temperatureHighTime": 1577663400,
                "temperatureLow": 44.3,
                "temperatureLowTime": 1577713620,
                "apparentTemperatureHigh": 52.34,
                "apparentTemperatureHighTime": 1577663400,
                "apparentTemperatureLow": 39.05,
                "apparentTemperatureLowTime": 1577714880,
                "dewPoint": 39.31,
                "humidity": 0.74,
                "pressure": 1022.6,
                "windSpeed": 5.07,
                "windGust": 10.86,
                "windGustTime": 1577676900,
                "windBearing": 30,
                "cloudCover": 0.87,
                "uvIndex": 2,
                "uvIndexTime": 1577649480,
                "visibility": 10,
                "ozone": 338.3,
                "temperatureMin": 42.85,
                "temperatureMinTime": 1577631300,
                "temperatureMax": 52.84,
                "temperatureMaxTime": 1577663400,
                "apparentTemperatureMin": 40.16,
                "apparentTemperatureMinTime": 1577630760,
                "apparentTemperatureMax": 52.34,
                "apparentTemperatureMaxTime": 1577663400,
            },
        ],
    },
    "offset": -8,
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
