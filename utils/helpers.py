import os
import requests
from supybot import log
from dotenv import load_dotenv
from typing import Union, Dict, List, Any
from ..models.users import User
from .errors import LocationNotFound, WeatherNotFound
from os.path import dirname, abspath, join
from cachetools import cached, LRUCache, TTLCache


path: str = dirname(abspath(__file__))
env_path: str = join(path, "..", ".env")
load_dotenv(dotenv_path=env_path)

lru_cache = LRUCache(maxsize=32)
ttl_cache = TTLCache(maxsize=64, ttl=900)


def check_user(nick: str) -> Union[User, None]:
    user: Union[User, None]
    try:
        user = User.get(User.nick == nick)
    except User.DoesNotExist:
        user = None

    return user


@cached(cache=lru_cache)
def find_geolocation(location: str) -> Dict[str, str]:
    payload = {
        "access_key": os.getenv("WS_API_KEY"),
        "query": location,
    }
    response = requests.get(
        "http://api.weatherstack.com/current", params=payload
    )
    response.raise_for_status()

    res_data = response.json()
    if response.status_code == 200 and "error" in res_data:
        log.error(f"geolocation: {res_data['error']['info']}")
        raise LocationNotFound("Unable to find this location.")

    res_location: Dict[str, Union[str, float]] = res_data.get("location")
    name: str = res_location.get("name", "New York")
    region: str = res_location.get("region", "New York")
    lat: str = res_location.get("lat", 40.714)
    long: str = res_location.get("lon", -74.006)
    coordinates = f"{lat},{long}"

    return {"location": name, "region": region, "coordinates": coordinates}


@cached(cache=ttl_cache)
def find_current_weather(coordinates: str) -> Dict[str, Any]:
    darksky_key: str = os.getenv("DS_API_KEY")
    payload = {"exclude": "minutely,hourly,flags"}
    response = requests.get(
        f"https://api.darksky.net/forecast/{darksky_key}/{coordinates}",
        params=payload,
    )
    response.raise_for_status()

    return response.json()


def display_format(
    location: str, region: str, data: Dict[str, Any], format: int = 1
) -> str:
    current: Dict[Union[str, float]] = data.get("currently")
    forecast: Dict[str, List[Dict]] = data.get("daily", {}).get("data")

    if not current or not forecast:
        log.error(
            "JSON data does not have current or forecast keys", exc_info=True
        )
        raise WeatherNotFound("Unable to find the weather at this time.")

    temp: float = current.get("temperature")
    feels: float = current.get("apparentTemperature")
    wind_spd: float = current.get("windSpeed")
    forecast_high = forecast[0].get("temperatureHigh")
    forecast_low = forecast[0].get("temperatureLow")

    # Format to display imperial or metric units first.
    # e.g. 1 = imperial, 2 = metric, default is imperial.
    if format == 1:
        temperature: str = f"{temp:.1f}F/{(temp - 32)/1.8:.1f}C"
        feels_like: str = f"{feels:.1f}F/{(feels - 32)/1.8:.1f}C"
        high = f"{forecast_high}F/{(forecast_high - 32)/1.8:.1f}C"
        low = f"{forecast_low}F/{(forecast_low - 32)/1.8:.1f}C"
        wind: str = f"{wind_spd:.1f}mph/{wind_spd * 1.609344:.1f}kph"
    else:
        temperature: str = f"{(temp - 32)/1.8:.1f}/C{temp:.1f}F"
        feels_like: str = f"{(feels - 32)/1.8:.1f}C/{feels:.1f}F"
        high = f"{(forecast_high - 32)/1.8:.1f}C/{forecast_high}F"
        low = f"{(forecast_low - 32)/1.8:.1f}C/{forecast_low}F"
        wind: str = f"{wind_spd * 1.609344:.1f}kph/{wind_spd:.1f}mph"

    place: str = f"{location}, {region}"
    condition: str = current.get("summary", "N/A")
    humidity: str = f"{int(current.get('humidity') * 100)}"
    wind_dir: str = _format_directions(current.get("windBearing"))
    summary = forecast[0].get("summary", "N/A")

    display: str = (
        f"\x02{place}\x02 :: {condition} {temperature} (Humidity: {humidity}%)"
        f" | \x02Feels like:\x02 {feels_like} | \x02Wind\x02: {wind_dir} at "
        f"{wind} | \x02Today:\x02 {summary} High {high} - Low {low}"
    )

    return display


def _format_directions(degrees: float) -> str:
    if not degrees:
        return "N/A"

    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    formula = round(degrees / (360.0 / len(directions))) % len(directions)

    return directions[formula]
