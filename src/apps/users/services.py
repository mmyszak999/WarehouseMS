from typing import Any

from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.schemas import (
    UserOutputSchema,
    UserLoginInputSchema
)
from src.core.utils.crypt import passwd_context, hash_user_password
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate


def authenticate(user_login_schema: UserLoginInputSchema, session: AsyncSession) -> User:
    login_data = user_login_schema.dict()
    user = session.scalar(
        select(User).filter(User.email == login_data["email"]).limit(1)
    )
    if not (user or passwd_context.verify(login_data["password"], user.password)):
        raise AuthenticationException("Invalid Credentials")
    """if not user.is_active:
        raise AccountNotActivatedException("email", login_data["email"])"""
    return user


def get_access_token_schema(
    user_login_schema: UserLoginInputSchema, session: AsyncSession, auth_jwt: AuthJWT
) -> str:
    user = authenticate(user_login_schema, session=session)
    email = user.email
    access_token = auth_jwt.create_access_token(subject=email, algorithm="HS256")

    return AccessTokenOutputSchema(access_token=access_token)



async def get_all_users(
    session: AsyncSession, page_params: PageParams) -> PagedResponseSchema[UserOutputSchema]:
    query = select(User)
    return await paginate(
        query=query,
        response_schema=UserOutputSchema,
        table=User,
        page_params=page_params,
        session=session,
    )