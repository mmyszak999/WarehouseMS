from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.warehouse.schemas import (
    WarehouseInputSchema,
    WarehouseOutputSchema,
    WarehouseUpdateSchema,
    WarehouseBaseOutputSchema
)
from src.apps.warehouse.services import (
    create_warehouse,
    delete_single_warehouse,
    get_all_warehouses,
    get_single_warehouse,
    update_single_warehouse,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

warehouse_router = APIRouter(prefix="/warehouse", tags=["warehouse"])


@warehouse_router.post(
    "/",
    response_model=WarehouseInputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_warehouse(
    warehouse: WarehouseInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> WarehouseOutputSchema:
    await check_if_staff(request_user)
    return await create_warehouse(session, warehouse)


@warehouse_router.get(
    "/",
    response_model=PagedResponseSchema[WarehouseBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_warehouses(
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[WarehouseBaseOutputSchema]:
    return await get_all_warehouses(session, page_params)


@warehouse_router.get(
    "/{warehouse_id}",
    response_model=WarehouseOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_warehouse(
    warehouse_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> WarehouseOutputSchema:
    await check_if_staff(request_user)
    return await get_single_warehouse(session, warehouse_id)


@warehouse_router.patch(
    "/{warehouse_id}",
    response_model=WarehouseOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_warehouse(
    warehouse_id: str,
    warehouse_input: WarehouseUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> WarehouseOutputSchema:
    await check_if_staff(request_user)
    return await update_single_warehouse(session, warehouse_input, warehouse_id)


@warehouse_router.delete(
    "/{warehouse_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_warehouse(
    warehouse_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    await delete_single_warehouse(session, warehouse_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
