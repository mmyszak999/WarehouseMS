from typing import Any


class ServiceException(Exception):
    pass

class DoesNotExist(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{class_name} with {field}={value} does not exist")


class AlreadyExists(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{class_name} with {field}={value} already exists")


class IsOccupied(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{field}={value} value of {class_name} is occupied")
        

class AuthenticationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AuthorizationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AccountNotActivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} has not been activated! "
            "Please check your mailbox to find the message with activation link "
            "If you think this is a mistake, contact or mail our support team!"
        )


class AccountAlreadyDeactivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} was already deactivated! "
        )


"""
if not user.is_active:
        raise AccountNotActivatedException("email", jwt_subject)
"""