import httpx


class BaseClientError(Exception):
    """Base client exception."""


class UserOrApikeyNotSetError(BaseClientError):
    def __init__(self) -> None:
        super().__init__("User or apikey didn't set")


class ApikeyNotSetError(BaseClientError):
    def __init__(self) -> None:
        super().__init__("Apikey didn't set")


class ClientRequestError(BaseClientError):
    def __init__(self, response: httpx.Response, message) -> None:
        super().__init__(message)
        self.response = response
