import os
import logging
import requests
from ..models.users import User
from functools import lru_cache
from dotenv import load_dotenv
from typing import Union, Dict, Union
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
    res_location: Dict[str, Union[str, int]] = res_data.get("location")
    name: str = res_location.get("name", "New York")
    region: str = res_location.get("region", "New York")
    lat: str = res_location.get('lat', 40.714)
    long: str = res_location.get('lon', -74.006)
    coordinates = f"{lat},{long}"

    return {"location": name, "region": region, "coordinates": coordinates}


def find_current_weather():
    pass
