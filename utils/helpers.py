import os
import logging
import requests
from .errors import LocationNotFound
from ..models.users import User
from functools import lru_cache
from dotenv import load_dotenv
from typing import Union, Dict
from os.path import dirname, abspath, join


path: str = dirname(abspath(__file__))
env_path: str = join(path, "..", ".env")
load_dotenv(dotenv_path=env_path)

log = logging.getLogger(__name__)


def check_user(nick: str) -> Union[User, None]:
    user: Union[User, None]
    try:
        user = User.get(User.nick == nick)
    except User.DoesNotExist:
        user = None

    return user


@lru_cache(maxsize=64)
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
        raise LocationNotFound("Unable to find this location.")

    res_location: Dict[str, Union[str, float]] = res_data.get("location")
    name: str = res_location.get("name", "New York")
    region: str = res_location.get("region", "New York")
    lat: str = res_location.get("lat", 40.714)
    long: str = res_location.get("lon", -74.006)
    coordinates = f"{lat},{long}"

    return {"location": name, "region": region, "coordinates": coordinates}


def find_current_weather(coordinates: str) -> Dict[str, Union[str, float]]:
    darksky_key: str = os.getenv("DS_API_KEY")
    payload = {"exclude": "minutely,hourly,flags"}
    response = requests.get(
        f"https://api.darksky.net/forecast/{darksky_key}/{coordinates}",
        params=payload,
    )
    response.raise_for_status()

    return response.json()
