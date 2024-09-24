from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from src.apps.users.models import User
from src.core.exceptions import (
    AccountNotActivatedException,
    AuthenticationException,
    PasswordNotSetException,
)
from src.dependencies.get_db import get_db
from src.settings.jwt_settings import AuthJWTSettings


async def authenticate_user(
    auth_jwt: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)
) -> User:
    auth_jwt.jwt_required()
    jwt_subject = auth_jwt.get_jwt_subject()
    user = await session.scalar(
        select(User)
        .options(
            load_only(
                User.email,
                User.is_active,
                User.has_password_set,
                User.id,
                User.is_staff,
                User.can_move_stocks,
                User.can_issue_stocks,
                User.can_recept_stocks,
            )
        )
        .filter(User.email == jwt_subject)
        .limit(1)
    )
    if not user:
        raise AuthenticationException("Cannot find user")
    if not user.is_active:
        raise AccountNotActivatedException("email", user.email)
    if not user.has_password_set:
        raise PasswordNotSetException

    return user


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()
