from typing import Any


class ServiceException(Exception):
    pass


class AuthenticationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")