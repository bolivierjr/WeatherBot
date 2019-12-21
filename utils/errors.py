from requests.exceptions import RequestException


class LocationNotFound(RequestException):
    pass
