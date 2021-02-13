import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

import requests
from supybot import log

from ..models.users import User
from .errors import LocationNotFound, WeatherNotFound
from .users import AnonymousUser


class WeatherAPI(ABC):
    """
    Base abstract class for weather APIs. This class can be subclassed to implement a new API
    service for weather data.

    Contains 2 abstract methods that must be implemented in the child class.

    Attributes:
        query: The location to query for weather results.
    """

    query: str

    @abstractmethod
    def find_current_weather(self, query: str) -> None:
        """
        Should find the current weather data from a query and prepare it to be formatted for display.
        """
        pass

    @abstractmethod
    def display_format(self) -> str:
        """
        Should format the weather data to be displayed on screen by a user.
        """
        pass


class OpenWeatherMapAPI(WeatherAPI):
    """
    Weather API class that uses Darksky and Weatherstack(for geolocation) to get weather data.

    Attributes:
        query: The location to query for weather results. e.g. 70119 or New Orleans, LA
        location: The city of the location queried.
        region: The region or state of location queried.
        coordinates: The coordinates of the location queried.
        data: The current weather data received back from the api.
    """

    def __init__(self, query: str):
        self.query = query
        self.location: Union[None, str] = None
        self.region: Union[None, str] = None
        self.coordinates: Union[None, str] = None
        self.data: Union[None, Dict[str, Any]] = None

    def find_geolocation(self) -> None:
        """
        Finds the location and coordinates and sets the class atttributes according to user's query.
        """
        payload = {
            "access_key": os.getenv("WS_API_KEY"),
            "query": self.query,
        }
        # https requires the paid tier, so we use http here.
        response: requests.Response = requests.get("http://api.weatherstack.com/current", params=payload)
        response.raise_for_status()

        res_data: Dict[str, Any] = response.json()
        if response.status_code == 200 and "error" in res_data:
            log.error("geolocation: %s", res_data["error"]["info"])
            raise LocationNotFound("Unable to find this location.")

        res_location: Dict[str, Union[str, float]] = res_data.get("location")
        lat: str = res_location.get("lat")
        long: str = res_location.get("lon")

        # Sets the location attributes, if region is not found, it will use the country
        # name. If no country name is found, it will then throw an exception.
        self.location: str = res_location.get("name")
        self.region: str = res_location.get("region").strip() or res_location.get("country")
        if not self.region:
            raise LocationNotFound("Unable to find this location.")
        self.coordinates = f"{lat},{long}"

    def format_directions(self, degrees: Union[int, None]) -> str:
        """
        Returns back the cardinal direction of the wind given the degrees from weather data.

        Args:
            degrees: Wind direction given in degrees.

        Returns:
            Cardinal direction of the wind.
        """
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
        formula: int = round(degrees / (360.0 / len(directions))) % len(directions)

        return directions[formula]

    def find_current_weather(self, user: Union[User, AnonymousUser]) -> None:
        """
        Returns the current weather found of a user's location query and sets the data class attribute.
        """
        if not self.query and not isinstance(user, AnonymousUser):
            self.location = user.location
            self.region = user.region
            self.coordinates = user.coordinates
        else:
            self.find_geolocation()

        lat, long = self.coordinates.split(",")
        payload = {
            "exclude": "minutely,hourly",
            "units": "imperial",
            "appid": os.getenv("OWM_API_KEY"),
            "lat": lat,
            "lon": long,
        }
        response = requests.get(f"https://api.openweathermap.org/data/2.5/onecall", params=payload)
        response.raise_for_status()

        self.data: Dict[str, Any] = response.json()

    def display_format(self, format: int = 1) -> str:
        """
        Takes the data that was queried and formats it to display to the user.

        Args:
            format(optional): The format you want to display the weather with.
                e.g. imperial first or metric - F/C or C/F

        Returns:
            A formatted string to display of the current weather.
        """
        current: Dict[Union[str, float]] = self.data.get("current")
        forecast: Dict[str, List[Dict]] = self.data.get("daily")
        if not current or not forecast:
            log.error("JSON data does not have current or forecast keys")
            raise WeatherNotFound("Unable to find the weather at this time.")

        temp: float = current.get("temp")
        feels: float = current.get("feels_like")
        wind_spd: float = current.get("wind_speed")
        forecast_high: float = forecast[0].get("temp").get("max")
        forecast_low: float = forecast[0].get("temp").get("min")

        # Format to display imperial or metric units first.
        # e.g. 1 = imperial, 2 = metric, default is imperial.
        if format == 1:
            temperature = f"{temp:.1f}F/{(temp - 32)/1.8:.1f}C"
            feels_like = f"{feels:.1f}F/{(feels - 32)/1.8:.1f}C"
            high = f"{forecast_high:.1f}F/{(forecast_high - 32)/1.8:.1f}C"
            low = f"{forecast_low:.1f}F/{(forecast_low - 32)/1.8:.1f}C"
            wind = f"{wind_spd:.1f}mph/{wind_spd * 1.609344:.1f}kph"
        else:
            temperature = f"{(temp - 32)/1.8:.1f}C/{temp:.1f}F"
            feels_like = f"{(feels - 32)/1.8:.1f}C/{feels:.1f}F"
            high = f"{(forecast_high - 32)/1.8:.1f}C/{forecast_high:.1f}F"
            low = f"{(forecast_low - 32)/1.8:.1f}C/{forecast_low:.1f}F"
            wind = f"{wind_spd * 1.609344:.1f}kph/{wind_spd:.1f}mph"

        place = f"{self.location}, {self.region}"
        condition: str = current.get("weather")[0].get("description").capitalize()
        humidity = f"{current.get('humidity')}"
        wind_dir: str = self.format_directions(current.get("wind_deg"))
        summary: str = forecast[0].get("weather")[0].get("description").capitalize()

        display = (
            f"\x02{place}\x02 :: {condition} {temperature} (Humidity: {humidity}%) | \x02Feels like\x02: {feels_like} "
            f"| \x02Wind\x02: {wind_dir} at {wind} | \x02Today\x02: {summary}. High {high} - Low {low}"
        )

        return display

    def __repr__(self) -> str:
        return f"<OpenWeatherMapAPI {self.query}>"
