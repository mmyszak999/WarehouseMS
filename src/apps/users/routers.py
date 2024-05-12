from typing import Union

from fastapi import BackgroundTasks, Depends, Request, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession


from src.apps.users.models import User
from src.apps.users.schemas import (
    UserOutputSchema,
)
from src.apps.users.services import (
    get_all_users
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get(
    "/",
    response_model=PagedResponseSchema[UserOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends()
) -> PagedResponseSchema[UserOutputSchema]:
    return await get_all_users(session, page_params)

