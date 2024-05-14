from typing import Any

from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.schemas import (
    UserOutputSchema,
    UserLoginInputSchema,
    UserInputSchema,
    UserInfoOutputSchema,
    UserUpdateSchema
)
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.core.utils.crypt import passwd_context, hash_user_password
from src.core.utils.email import confirm_token
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.exceptions import (
    AuthenticationException,
    DoesNotExist,
    ServiceException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AccountAlreadyActivatedException
)
from src.core.utils.orm import if_exists


async def manage_activation_status(
    session: AsyncSession, field: str, value: Any,
    request_user_id: str = None, activate: bool = True) -> None:
    if not (user_object := (await if_exists(User, field, value, session))):
        raise DoesNotExist(User.__name__, "id", user_id)
    
    if activate and user_object.is_active:
        raise AccountAlreadyActivatedException("email", user_object.email)
    
    if (not activate) and (not user_object.is_active) :
        raise AccountAlreadyDeactivatedException("email", user_object.email)
    
    user_object.is_active = activate
    session.add(user_object)
    
    await session.commit()


async def activate_single_user(session: AsyncSession, field: str, value: Any) -> None:
    await manage_activation_status(session, field, value)


async def deactivate_single_user(session: AsyncSession, user_id: str, request_user_id: str) -> None:
    if user_id == request_user_id:
        raise Exception("You can't deactivate your account!")
    
    await manage_activation_status(session, "id", user_id, request_user_id=request_user_id, activate=False)


async def activate_account_service(session: AsyncSession, token: str) -> None:
    emails = await confirm_token(token)
    current_email = emails[0]
    await activate_single_user(session, "email", current_email)


async def set_user_password(session: AsyncSession, token):
    pass