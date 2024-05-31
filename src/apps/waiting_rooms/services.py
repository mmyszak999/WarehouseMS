from typing import Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.schemas import (
    WaitingRoomBasicOutputSchema,
    WaitingRoomOutputSchema,
    WaitingRoomInputSchema,
    WaitingRoomUpdateSchema
)
from src.apps.stocks.models import Stock
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    MissingWaitingRoomDataException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists



async def create_waiting_room(
    session: AsyncSession, waiting_room_input: WaitingRoomInputSchema
) -> WaitingRoomOutputSchema:
    waiting_room_input = waiting_room_input.dict()
    new_waiting_room = WaitingRoom(
        max_stocks=waiting_room_input.pop('max_stocks'),
        max_weight=waiting_room_input.pop('max_weight')
    )

    session.add(new_waiting_room)
    await session.commit()
    await session.refresh(new_waiting_room)

    return WaitingRoomOutputSchema.from_orm(new_waiting_room)


async def get_single_waiting_room(
    session: AsyncSession,
    waiting_room_id: int,
    output_schema: BaseModel = WaitingRoomOutputSchema
) -> WaitingRoomOutputSchema:
    if not (waiting_room_object := await if_exists(WaitingRoom, "id", waiting_room_id, session)):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)

    return output_schema.from_orm(waiting_room_object)


async def get_all_waiting_rooms(
    session: AsyncSession, page_params: PageParams, output_schema: BaseModel = WaitingRoomBasicOutputSchema
) -> Union[
    PagedResponseSchema[WaitingRoomBasicOutputSchema],
    PagedResponseSchema[WaitingRoomOutputSchema]
    ]:
    query = select(WaitingRoom)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=WaitingRoom,
        page_params=page_params,
        session=session,
    )


async def update_single_waiting_room(
    session: AsyncSession, waiting_room_input: WaitingRoomUpdateSchema, waiting_room_id: int
) -> WaitingRoomOutputSchema:
    if not (waiting_room_object := await if_exists(WaitingRoom, "id", waiting_room_id, session)):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)

    waiting_room_data = waiting_room_input.dict(exclude_unset=True, exclude_none=True)

    if new_max_weight := waiting_room_data.get('max_weight'):
        if new_max_weight < waiting_room_object.current_stock_weight:
            raise Exception('too less weight')
    
    if new_max_stocks := waiting_room_data.get('max_stocks'):
        if new_max_stocks < waiting_room_object.occupied_slots:
            raise Exception('too less space for current stocks')
        
    
    if waiting_room_data:
        statement = update(WaitingRoom).filter(WaitingRoom.id == waiting_room_id).values(**waiting_room_data)

        await session.execute(statement)
        await session.commit()
        await session.refresh(waiting_room_object)

    return await get_single_waiting_room(session, waiting_room_id=waiting_room_id)
