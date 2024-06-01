from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.waiting_rooms.schemas import (
    WaitingRoomInputSchema,
    WaitingRoomOutputSchema,
    WaitingRoomUpdateSchema,
    WaitingRoomBasicOutputSchema
)
from src.apps.waiting_rooms.services import (
    create_waiting_room,
    delete_single_waiting_room,
    get_all_waiting_rooms,
    get_single_waiting_room,
    update_single_waiting_room,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

waiting_room_router = APIRouter(prefix="/waiting_rooms", tags=["waiting_room"])


@waiting_room_router.post(
    "/",
    response_model=WaitingRoomOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_waiting_room(
    waiting_room: WaitingRoomInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> WaitingRoomOutputSchema:
    await check_if_staff(request_user)
    return await create_waiting_room(session, waiting_room)


@waiting_room_router.get(
    "/",
    response_model=PagedResponseSchema[WaitingRoomBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_waiting_rooms(
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[WaitingRoomBasicOutputSchema]:
    return await get_all_waiting_rooms(session, page_params)


@waiting_room_router.get(
    "/{waiting_room_id}",
    response_model=WaitingRoomOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_waiting_room(
    waiting_room_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> WaitingRoomOutputSchema:
    if (await check_if_staff(request_user)):
        return await get_single_waiting_room(session, waiting_room_id)
    return await get_single_waiting_room(
        session, waiting_room_id, output_schema=WaitingRoomBasicOutputSchema
    )



@waiting_room_router.patch(
    "/{waiting_room_id}",
    response_model=WaitingRoomOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_waiting_room(
    waiting_room_id: str,
    waiting_room_input: WaitingRoomUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> WaitingRoomOutputSchema:
    await check_if_staff(request_user)
    return await update_single_waiting_room(session, waiting_room_input, waiting_room_id)


@waiting_room_router.delete(
    "/{waiting_room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_waiting_room(
    waiting_room_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    await delete_single_waiting_room(session, waiting_room_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
