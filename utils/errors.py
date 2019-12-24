from requests.exceptions import RequestException


class LocationNotFound(RequestException):
    pass


class WeatherNotFound(RequestException):
    pass
