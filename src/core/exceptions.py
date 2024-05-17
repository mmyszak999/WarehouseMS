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
            "Please check your mailbox to find the message with activation link. "
            "If you think this is a mistake, contact or mail our support team!"
        )


class AccountAlreadyDeactivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} was already deactivated!"
        )


class AccountAlreadyActivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} was already activated!"
        )


class UserCantDeactivateTheirAccountException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"User can't deactivate their account!")


class UserCantActivateTheirAccountException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            f"User can't activate their account by other way than using activation link when account created! "
            "If necessary, please contact our support team! "
        )


class PasswordAlreadySetException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"This account already has its password set! ")


class PasswordNotSetException(ServiceException):
    def __init__(self) -> None:
        super().__init__(f"This account hasn't got the password set! ")
