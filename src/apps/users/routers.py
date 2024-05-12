from typing import Union

from fastapi import BackgroundTasks, Depends, Request, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.users.models import User
from src.apps.users.schemas import (
    UserOutputSchema,
    UserLoginInputSchema
)
from src.apps.users.services import (
    get_all_users,
    get_access_token_schema
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=AccessTokenOutputSchema
)
async def login_user(
    user_login_schema: UserLoginInputSchema,
    auth_jwt: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_db),
) -> AccessTokenOutputSchema:
    return await get_access_token_schema(user_login_schema, session, auth_jwt)


@user_router.get(
    "/",
    response_model=PagedResponseSchema[UserOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user)
) -> PagedResponseSchema[UserOutputSchema]:
    return await get_all_users(session, page_params)

