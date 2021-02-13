import os
from typing import Dict, Union

from cachetools import TTLCache, cached

from ..models.users import User
from .users import AnonymousUser
from .weather import OpenWeatherMapAPI, WeatherAPI

# Configurable ttl cache settings that you can change
# through environment variables.
maxsize = int(os.getenv("TTL_CACHE_MAX_SIZE"))
ttl = int(os.getenv("TTL_CACHE_TIME"))

ttl_cache = TTLCache(maxsize=maxsize, ttl=ttl)


@cached(cache=ttl_cache)
def query_location(query: str) -> Dict[str, str]:
    """
    Client function to get a user's queried location.

    Args:
        query: The location to query for the weather api.

    Returns:
        A dictionary of results of location, region and coordinates.
    """
    weather = WeatherService(OpenWeatherMapAPI(query))
    return weather.get_location()


def query_current_weather(query: str, user: Union[User, AnonymousUser]) -> str:
    """
    Client function to get user's weather display.

    Args:
        query: The location to query for the weather api.
        user: The user object found in the db or an anonymous user object.

    Returns:
        A formatted string to display of the weather to output.
    """
    weather = WeatherService(OpenWeatherMapAPI(query))
    return weather.get_current(user)


class WeatherService:
    """
    Weather service that takes in a weather api interface to query current
    weather and location.

    Attributes:
        weather_api: A class that implements the WeatherAPI interface.
    """

    def __init__(self, weather_api: WeatherAPI):
        self.weather_api = weather_api

    def get_current(self, user: Union[User, AnonymousUser]) -> str:
        """
        Gets the current weather data and formats it to display to a user.

        Args:
            user: The user object found in the db or an anonymous user object.

        Returns:
             A formatted string to display of the weather to output.
        """
        self.weather_api.find_current_weather(user)
        return self.weather_api.display_format(user.format)

    def get_location(self) -> Dict[str, str]:
        """
        Gets the location, region, and coordinate values that were queried by the user.

        Returns:
            A dictionary of location results that was queried by a user.
        """
        self.weather_api.find_geolocation()
        return {
            "location": self.weather_api.location,
            "region": self.weather_api.region,
            "coordinates": self.weather_api.coordinates,
        }

    def __repr__(self) -> str:
        return f"<WeatherService {self.weather_api}>"
