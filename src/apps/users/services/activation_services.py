from typing import Any

from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.emails.services import retrieve_email_from_token
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.users.models import User
from src.apps.users.schemas import (
    UserInfoOutputSchema,
    UserInputSchema,
    UserLoginInputSchema,
    UserOutputSchema,
    UserPasswordSchema,
    UserUpdateSchema,
)
from src.core.exceptions import (
    AccountAlreadyActivatedException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AuthenticationException,
    DoesNotExist,
    PasswordAlreadySetException,
    ServiceException,
    UserCantDeactivateTheirAccountException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.crypt import hash_user_password, passwd_context
from src.core.utils.email import confirm_token
from src.core.utils.orm import if_exists


async def manage_activation_status(
    session: AsyncSession,
    field: str,
    value: Any,
    request_user_id: str = None,
    activate: bool = True,
) -> None:
    if not (user_object := (await if_exists(User, field, value, session))):
        raise DoesNotExist(User.__name__, "id", user_id)

    if activate and user_object.is_active:
        raise AccountAlreadyActivatedException("email", user_object.email)

    if (not activate) and (not user_object.is_active):
        raise AccountAlreadyDeactivatedException("email", user_object.email)

    user_object.is_active = activate
    session.add(user_object)

    await session.commit()


async def activate_single_user(
    session: AsyncSession, user_id: str, request_user_id: str
) -> None:
    if user_id == request_user_id:
        raise UserCantActivateTheirAccountException

    await manage_activation_status(
        session, "id", user_id, request_user_id=request_user_id
    )


async def activate_single_user_by_link(
    session: AsyncSession, field: str, value: Any
) -> None:
    await manage_activation_status(session, field, value)


async def deactivate_single_user(
    session: AsyncSession, user_id: str, request_user_id: str
) -> None:
    if user_id == request_user_id:
        raise UserCantDeactivateTheirAccountException

    await manage_activation_status(
        session, "id", user_id, request_user_id=request_user_id, activate=False
    )


async def set_user_password(
    session: AsyncSession, user_email: str, password_schema: UserPasswordSchema
) -> None:
    if not (user_object := (await if_exists(User, "email", user_email, session))):
        raise DoesNotExist(User.__name__, "email", user_email)

    if user_object.has_password_set:
        raise PasswordAlreadySetException

    user_passwords = password_schema.dict()

    if user_passwords.pop("password_repeat"):
        user_password = await hash_user_password(
            password=user_passwords.pop("password")
        )

    user_object.password = user_password
    user_object.has_password_set = True

    session.add(user_object)

    await session.commit()
    await session.refresh(user_object)


async def activate_account_service(
    session: AsyncSession, token: str, user_passwords: UserPasswordSchema
) -> None:
    user_email = await retrieve_email_from_token(session, token)
    await set_user_password(session, user_email, user_passwords)
    await activate_single_user_by_link(session, "email", user_email)
