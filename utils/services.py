from typing import Dict

from cachetools import TTLCache, cached

from .weather import DarkskyAPI, WeatherAPI

ttl_cache = TTLCache(maxsize=64, ttl=900)


@cached(cache=ttl_cache)
def query_location(query: str) -> Dict[str, str]:
    """
    Client function to get a user's queried location.

    Args:
        query: The location to query for the weather api.

    Returns:
        A dictionary of results of location, region and coordinates.
    """
    weather = WeatherService(DarkskyAPI(query))
    return weather.get_location()


@cached(cache=ttl_cache)
def query_current_weather(query: str, format: int = 1) -> str:
    """
    Client function to get user's weather display.

    Args:
        query: The location to query for the weather api.
        format(optional): The format you want to display the weather with.
            e.g. imperial first or metric - F/C or C/F

    Returns:
        A formatted string to display of the weather to output.
    """
    weather = WeatherService(DarkskyAPI(query))
    return weather.get_current(format)


class WeatherService:
    """
    Weather service that takes in a weather api interface to query current
    weather and location.

    Attributes:
        weather_api: A class that implements the WeatherAPI interface.
    """

    def __init__(self, weather_api: WeatherAPI):
        self.weather_api = weather_api

    def get_current(self, format: int = 1) -> str:
        """
        Returns back a formatted display of the weather to output.

        Args:
            format(optional): The format you want to display the weather with.
                e.g. imperial first or metric - F/C or C/F

        Returns:
             A formatted string to display of the weather to output.
        """
        self.weather_api.find_current_weather()
        return self.weather_api.display_format(format)

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
