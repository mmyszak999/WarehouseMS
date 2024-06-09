from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.stocks.models import Stock, UserStock
from src.apps.stocks.schemas.user_stock_schemas import (
    UserStockInputSchema,
    UserStockOutputSchema,
)
from src.apps.stocks.services.user_stock_services import (
    get_all_user_stocks,
    get_single_user_stock,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_has_permission
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

user_stock_router = APIRouter(prefix="/user-stocks", tags=["user-stock"])


@user_stock_router.get(
    "/",
    response_model=PagedResponseSchema[UserStockOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_stocks(
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[UserStockOutputSchema]:
    await check_if_staff_or_has_permission(request_user, "can_move_stocks")
    return await get_all_user_stocks(session, page_params)


@user_stock_router.get(
    "/{user_stock_id}",
    response_model=UserStockOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_stock(
    user_stock_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
    page_params: PageParams = Depends(),
) -> UserStockOutputSchema:
    await check_if_staff_or_has_permission(request_user, "can_move_stocks")
    return await get_single_user_stock(session, user_stock_id)
