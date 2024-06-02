from typing import Union
from decimal import Decimal

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
from src.apps.stocks.schemas import StockWaitingRoomInputSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    TooLittleWaitingRoomSpaceException,
    TooLittleWaitingRoomWeightException,
    WaitingRoomIsNotEmptyException,
    CannotMoveIssuedStockException,
    StockAlreadyInWaitingRoomException,
    NoAvailableSlotsInWaitingRoomException,
    NoAvailableWeightInWaitingRoomException,
    ServiceException
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
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[WaitingRoomBasicOutputSchema]:
    query = select(WaitingRoom)

    return await paginate(
        query=query,
        response_schema=WaitingRoomBasicOutputSchema,
        table=WaitingRoom,
        page_params=page_params,
        session=session,
    )


async def manage_waiting_room_state(
    waiting_room_object: WaitingRoom,
    max_weight: Decimal = None,
    max_stocks: int = None,
    stocks_involved: bool = False,
    decrease_values: bool = False,
    stock_object: Stock = None
) -> WaitingRoom:
    multiplier = -1 if decrease_values else 1
    if stocks_involved:
        if stock_object is None:
            raise ServiceException("Stock object was not provided! ")
        waiting_room_object.available_slots -= multiplier
        waiting_room_object.occupied_slots += multiplier
        waiting_room_object.current_stock_weight += (multiplier * stock_object.weight)
        waiting_room_object.available_stock_weight -= (multiplier * stock_object.weight)
    else:
        if max_weight is not None:
            new_available_weight = max_weight - waiting_room_object.current_stock_weight
            waiting_room_object.available_stock_weight = new_available_weight
        if max_stocks is not None:
            new_available_slots = max_stocks - waiting_room_object.occupied_slots
            waiting_room_object.available_slots = new_available_slots
        
    return waiting_room_object


async def update_single_waiting_room(
    session: AsyncSession, waiting_room_input: WaitingRoomUpdateSchema, waiting_room_id: int
) -> WaitingRoomOutputSchema:
    if not (waiting_room_object := await if_exists(WaitingRoom, "id", waiting_room_id, session)):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)

    waiting_room_data = waiting_room_input.dict(exclude_unset=True, exclude_none=True)

    if new_max_weight := waiting_room_data.get('max_weight'):
        if new_max_weight < waiting_room_object.current_stock_weight:
            raise TooLittleWaitingRoomWeightException(
                new_max_weight, waiting_room_object.current_stock_weight
            )
    
    if new_max_stocks := waiting_room_data.get('max_stocks'):
        if new_max_stocks < waiting_room_object.occupied_slots:
            raise TooLittleWaitingRoomSpaceException(
                new_max_stocks, waiting_room_object.occupied_slots
            )
    
    waiting_room_object = await manage_waiting_room_state(
        waiting_room_object, new_max_weight, new_max_stocks
    )
    session.add(waiting_room_object)
    
    if waiting_room_data:
        statement = update(WaitingRoom).filter(WaitingRoom.id == waiting_room_id).values(**waiting_room_data)

        await session.execute(statement)
        await session.commit()
        await session.refresh(waiting_room_object)

    return await get_single_waiting_room(session, waiting_room_id=waiting_room_id)


async def delete_single_waiting_room(session: AsyncSession, waiting_room_id: str):
    if not (waiting_room_object := await if_exists(WaitingRoom, "id", waiting_room_id, session)):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)
    
    if waiting_room_object.occupied_slots:
        raise WaitingRoomIsNotEmptyException
    statement = delete(WaitingRoom).filter(WaitingRoom.id == waiting_room_id)
    result = await session.execute(statement)
    await session.commit()

    return result


async def add_single_stock_to_waiting_room(
    session: AsyncSession, waiting_room_id: str, stock_schema: StockWaitingRoomInputSchema
) -> dict[str, str]:
    if not (waiting_room_object := await if_exists(WaitingRoom, "id", waiting_room_id, session)):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)
    
    stock_id = stock_schema.id
    if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
        raise DoesNotExist(Stock.__name__, "id", stock_id)
    
    if stock_object.is_issued:
        raise CannotMoveIssuedStockException
    
    if stock_object.waiting_room_id is not None:
        raise StockAlreadyInWaitingRoomException
    
    if waiting_room_object.occupied_slots == waiting_room_object.max_stocks:
        raise NoAvailableSlotsInWaitingRoomException
    
    if (waiting_room_object.current_stock_weight + stock_object.weight) > waiting_room_object.max_weight:
        raise NoAvailableWeightInWaitingRoomException
    
    
    waiting_room_object = await manage_waiting_room_state(
        waiting_room_object, stocks_involved=True, stock_object=stock_object
    )
    session.add(waiting_room_object)
    
    stock_object.waiting_room_id = waiting_room_object.id
    session.add(stock_object)
    await session.commit()

    return {"message": "Stock was successfully add to the waiting room! "}
