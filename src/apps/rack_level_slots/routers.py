from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_level_slots.schemas import (
    RackLevelSlotBaseOutputSchema,
    RackLevelSlotInputSchema,
    RackLevelSlotOutputSchema,
    RackLevelSlotUpdateSchema,
)
from src.apps.rack_level_slots.services import (
    activate_single_rack_level_slot,
    create_rack_level_slot,
    deactivate_single_rack_level_slot,
    get_all_rack_level_slots,
    get_single_rack_level_slot,
    update_single_rack_level_slot,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

rack_level_slot_router = APIRouter(prefix="/rack-level-slots", tags=["rack_level_slot"])


@rack_level_slot_router.post(
    "/",
    response_model=RackLevelSlotOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_rack_level_slot(
    rack_level_slot: RackLevelSlotInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> RackLevelSlotOutputSchema:
    await check_if_staff(request_user)
    return await create_rack_level_slot(session, rack_level_slot)


@rack_level_slot_router.get(
    "/",
    response_model=Union[
        PagedResponseSchema[RackLevelSlotBaseOutputSchema],
        PagedResponseSchema[RackLevelSlotOutputSchema],
    ],
    status_code=status.HTTP_200_OK,
)
async def get_rack_level_slots(
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
    PagedResponseSchema[RackLevelSlotBaseOutputSchema],
    PagedResponseSchema[RackLevelSlotOutputSchema],
]:
    return await get_all_rack_level_slots(session, page_params)


@rack_level_slot_router.get(
    "/{rack_level_slot_id}",
    response_model=Union[RackLevelSlotBaseOutputSchema, RackLevelSlotOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_rack_level_slot(
    rack_level_slot_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[RackLevelSlotBaseOutputSchema, RackLevelSlotOutputSchema]:
    if request_user.is_staff or request_user.can_move_stocks:
        return await get_single_rack_level_slot(session, rack_level_slot_id)
    return await get_single_rack_level_slot(
        session, rack_level_slot_id, output_schema=RackLevelSlotBaseOutputSchema
    )


@rack_level_slot_router.patch(
    "/{rack_level_slot_id}",
    response_model=RackLevelSlotOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_rack_level_slot(
    rack_level_slot_id: str,
    rack_level_slot_input: RackLevelSlotUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> RackLevelSlotOutputSchema:
    await check_if_staff(request_user)
    return await update_single_rack_level_slot(
        session, rack_level_slot_input, rack_level_slot_id
    )


@rack_level_slot_router.patch(
    "/{rack_level_slot_id}/activate",
    status_code=status.HTTP_200_OK,
)
async def activate_rack_level_slot(
    rack_level_slot_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    await check_if_staff(request_user)
    result = await activate_single_rack_level_slot(session, rack_level_slot_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@rack_level_slot_router.patch(
    "/{rack_level_slot_id}/deactivate",
    status_code=status.HTTP_200_OK,
)
async def deactivate_rack_level_slot(
    rack_level_slot_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    await check_if_staff(request_user)
    result = await deactivate_single_rack_level_slot(session, rack_level_slot_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
