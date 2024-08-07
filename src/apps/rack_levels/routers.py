from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_level_slots.schemas import (
    RackLevelSlotBaseOutputSchema,
    RackLevelSlotOutputSchema,
)
from src.apps.rack_level_slots.services import (
    get_all_rack_level_slots,
    get_single_rack_level_slot,
)
from src.apps.rack_levels.schemas import (
    RackLevelBaseOutputSchema,
    RackLevelInputSchema,
    RackLevelOutputSchema,
    RackLevelUpdateSchema,
)
from src.apps.rack_levels.services import (
    add_single_stock_to_rack_level,
    create_rack_level,
    delete_single_rack_level,
    get_all_rack_levels,
    get_single_rack_level,
    update_single_rack_level,
)
from src.apps.stocks.schemas.stock_schemas import StockRackLevelInputSchema
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_has_permission
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

rack_level_router = APIRouter(prefix="/rack_levels", tags=["rack_level"])


@rack_level_router.post(
    "/",
    response_model=RackLevelOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_rack_level(
    rack_level: RackLevelInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> RackLevelOutputSchema:
    await check_if_staff(request_user)
    return await create_rack_level(session, rack_level)


@rack_level_router.get(
    "/",
    response_model=Union[
        PagedResponseSchema[RackLevelBaseOutputSchema],
        PagedResponseSchema[RackLevelOutputSchema],
    ],
    status_code=status.HTTP_200_OK,
)
async def get_rack_levels(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
    PagedResponseSchema[RackLevelBaseOutputSchema],
    PagedResponseSchema[RackLevelOutputSchema],
]:
    return await get_all_rack_levels(
        session, page_params, query_params=request.query_params.multi_items()
    )


@rack_level_router.get(
    "/{rack_level_id}",
    response_model=Union[RackLevelOutputSchema, RackLevelBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_rack_level(
    rack_level_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[RackLevelOutputSchema, RackLevelBaseOutputSchema]:
    if request_user.is_staff or request_user.can_move_stocks:
        return await get_single_rack_level(session, rack_level_id)
    return await get_single_rack_level(
        session, rack_level_id, output_schema=RackLevelBaseOutputSchema
    )


@rack_level_router.get(
    "/{rack_level_id}/slots",
    response_model=Union[
        PagedResponseSchema[RackLevelSlotBaseOutputSchema],
        PagedResponseSchema[RackLevelSlotOutputSchema],
    ],
    status_code=status.HTTP_200_OK,
)
async def get_slots_in_the_rack_level(
    rack_level_id: str,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
    PagedResponseSchema[RackLevelSlotBaseOutputSchema],
    PagedResponseSchema[RackLevelSlotOutputSchema],
]:
    return await get_all_rack_level_slots(
        session, page_params, rack_level_id=rack_level_id
    )


@rack_level_router.get(
    "/{rack_level_id}/slots/{rack_level_slot_id}",
    response_model=Union[RackLevelSlotOutputSchema, RackLevelSlotBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_slot_from_the_rack_level(
    rack_level_id: str,
    rack_level_slot_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[RackLevelSlotOutputSchema, RackLevelSlotBaseOutputSchema]:
    if request_user.is_staff or request_user.can_move_stocks:
        return await get_single_rack_level_slot(
            session, rack_level_slot_id, rack_level_id=rack_level_id
        )
    return await get_single_rack_level_slot(
        session,
        rack_level_slot_id,
        output_schema=RackLevelSlotBaseOutputSchema,
        rack_level_id=rack_level_id,
    )


@rack_level_router.patch(
    "/{rack_level_id}",
    response_model=RackLevelOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_rack_level(
    rack_level_id: str,
    rack_level_input: RackLevelUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> RackLevelOutputSchema:
    await check_if_staff(request_user)
    return await update_single_rack_level(session, rack_level_input, rack_level_id)


@rack_level_router.delete(
    "/{rack_level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rack_level(
    rack_level_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    await delete_single_rack_level(session, rack_level_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@rack_level_router.patch(
    "/{rack_level_id}/add-stock",
    status_code=status.HTTP_200_OK,
)
async def add_stock_to_rack_level(
    rack_level_id: str,
    stock_schema: StockRackLevelInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    await check_if_staff_or_has_permission(request_user, "can_move_stocks")
    result = await add_single_stock_to_rack_level(
        session, rack_level_id, stock_schema, request_user.id
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
