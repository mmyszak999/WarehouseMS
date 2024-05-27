from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.stocks.schemas import (
    StockBasicOutputSchema,
    StockOutputSchema
    )

from src.apps.stocks.services import (
    get_all_available_stocks,
    get_all_stocks,
    get_single_stock
)
from src.apps.users.models import User
from src.apps.stocks.models import Stock
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff_or_has_permission, check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

stock_router = APIRouter(prefix="/stocks", tags=["stock"])


@stock_router.get(
    "/",
    response_model=PagedResponseSchema[StockBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_available_stocks(
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[StockBasicOutputSchema]:
    return await get_all_available_stocks(session, page_params)


@stock_router.get(
    "/all",
    response_model=PagedResponseSchema[StockOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_stocks(
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[StockOutputSchema]:
    await check_if_staff(request_user)
    return await get_all_stocks(session, page_params)


@stock_router.get(
    "/all/{stock_id}",
    response_model=StockOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_stock_as_staff(
    stock_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> StockOutputSchema:
    await check_if_staff(request_user)
    return await get_single_stock(session, stock_id, can_get_issued=True)


@stock_router.get(
    "/{stock_id}",
    response_model=StockBasicOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_stock(
    stock_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> StockOutputSchema:
    return await get_single_stock(session, stock_id)