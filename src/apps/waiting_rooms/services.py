from decimal import Decimal
from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_level_slots.services import manage_old_rack_level_slot_state
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas.stock_schemas import StockWaitingRoomInputSchema
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.schemas import (
    WaitingRoomBasicOutputSchema,
    WaitingRoomInputSchema,
    WaitingRoomOutputSchema,
    WaitingRoomUpdateSchema,
)
from src.apps.warehouse.models import Warehouse
from src.apps.warehouse.services import get_all_warehouses, manage_warehouse_state
from src.core.exceptions import (
    AlreadyExists,
    CannotMoveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    NoAvailableSlotsInWaitingRoomException,
    NoAvailableWeightInWaitingRoomException,
    NotEnoughWarehouseResourcesException,
    ServiceException,
    StockAlreadyInWaitingRoomException,
    TooLittleWaitingRoomSpaceException,
    TooLittleWaitingRoomWeightException,
    WaitingRoomIsNotEmptyException,
    WarehouseDoesNotExistException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def create_waiting_room(
    session: AsyncSession,
    waiting_room_input: WaitingRoomInputSchema,
    testing: bool = False,
) -> WaitingRoomOutputSchema:
    warehouses = await get_all_warehouses(session, PageParams())
    if not warehouses.total:
        raise WarehouseDoesNotExistException

    warehouse = await if_exists(Warehouse, "id", warehouses.results[0].id, session)

    if not warehouse.available_waiting_rooms:
        raise NotEnoughWarehouseResourcesException(resource="waiting rooms")

    waiting_room_input = waiting_room_input.dict()
    new_waiting_room = WaitingRoom(
        max_stocks=waiting_room_input.pop("max_stocks"),
        max_weight=waiting_room_input.pop("max_weight"),
        name=waiting_room_input.get("name"),
        warehouse_id=warehouse.id,
    )

    session.add(new_waiting_room)
    warehouse = await manage_warehouse_state(
        warehouse, adding_resources_to_warehouse=False, waiting_rooms_involved=True
    )
    session.add(warehouse)

    if testing:
        await session.commit()
        await session.refresh(new_waiting_room)
        return new_waiting_room

    await session.commit()
    await session.refresh(new_waiting_room)

    return WaitingRoomOutputSchema.from_orm(new_waiting_room)


async def get_single_waiting_room(
    session: AsyncSession,
    waiting_room_id: int,
    output_schema: BaseModel = WaitingRoomOutputSchema,
) -> Union[WaitingRoomOutputSchema, WaitingRoomBasicOutputSchema]:
    if not (
        waiting_room_object := await if_exists(
            WaitingRoom, "id", waiting_room_id, session
        )
    ):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)

    return output_schema.from_orm(waiting_room_object)


async def get_all_waiting_rooms(
    session: AsyncSession,
    page_params: PageParams,
    output_schema: BaseModel = WaitingRoomBasicOutputSchema,
    query_params: list[tuple] = None,
) -> Union[
    PagedResponseSchema[WaitingRoomBasicOutputSchema],
    PagedResponseSchema[WaitingRoomOutputSchema],
]:
    query = select(WaitingRoom)

    if query_params:
        query = filter_and_sort_instances(query_params, query, WaitingRoom)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=WaitingRoom,
        page_params=page_params,
        session=session,
    )


async def manage_waiting_room_state(
    waiting_room_object: WaitingRoom,
    max_weight: Decimal = None,
    max_stocks: int = None,
    stocks_involved: bool = False,
    adding_stock_to_waiting_room: bool = True,
    stock_weight: Decimal = None,
) -> WaitingRoom:
    multiplier = 1 if adding_stock_to_waiting_room else -1
    if stocks_involved:
        if stock_weight is None:
            raise ServiceException("Stock weight was not provided! ")
        waiting_room_object.available_slots -= multiplier
        waiting_room_object.occupied_slots += multiplier
        waiting_room_object.current_stock_weight += multiplier * stock_weight
        waiting_room_object.available_stock_weight -= multiplier * stock_weight
    else:
        if max_weight is not None:
            new_available_weight = max_weight - waiting_room_object.current_stock_weight
            waiting_room_object.available_stock_weight = new_available_weight
        if max_stocks is not None:
            new_available_slots = max_stocks - waiting_room_object.occupied_slots
            waiting_room_object.available_slots = new_available_slots

    return waiting_room_object


async def update_single_waiting_room(
    session: AsyncSession,
    waiting_room_input: WaitingRoomUpdateSchema,
    waiting_room_id: int,
) -> WaitingRoomOutputSchema:
    if not (
        waiting_room_object := await if_exists(
            WaitingRoom, "id", waiting_room_id, session
        )
    ):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)

    waiting_room_data = waiting_room_input.dict(exclude_unset=True, exclude_none=True)

    if new_max_weight := waiting_room_data.get("max_weight"):
        if new_max_weight < waiting_room_object.current_stock_weight:
            raise TooLittleWaitingRoomWeightException(
                new_max_weight, waiting_room_object.current_stock_weight
            )

    if new_max_stocks := waiting_room_data.get("max_stocks"):
        if new_max_stocks < waiting_room_object.occupied_slots:
            raise TooLittleWaitingRoomSpaceException(
                new_max_stocks, waiting_room_object.occupied_slots
            )

    waiting_room_object = await manage_waiting_room_state(
        waiting_room_object, new_max_weight, new_max_stocks
    )
    session.add(waiting_room_object)

    if waiting_room_data:
        statement = (
            update(WaitingRoom)
            .filter(WaitingRoom.id == waiting_room_id)
            .values(**waiting_room_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(waiting_room_object)

    return await get_single_waiting_room(session, waiting_room_id=waiting_room_id)


async def delete_single_waiting_room(session: AsyncSession, waiting_room_id: str):
    if not (
        waiting_room_object := await if_exists(
            WaitingRoom, "id", waiting_room_id, session
        )
    ):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)

    if waiting_room_object.stocks:
        raise WaitingRoomIsNotEmptyException
    statement = delete(WaitingRoom).filter(WaitingRoom.id == waiting_room_id)
    result = await session.execute(statement)

    warehouse = await if_exists(
        Warehouse, "id", waiting_room_object.warehouse_id, session
    )

    warehouse = await manage_warehouse_state(warehouse, waiting_rooms_involved=True)
    session.add(warehouse)
    await session.commit()

    return result


async def manage_old_waiting_room_state(
    session: AsyncSession,
    stock_object: Stock,
    old_waiting_room_object: WaitingRoom,
    old_waiting_room_id: str,
) -> WaitingRoom:
    old_waiting_room_object = await manage_waiting_room_state(
        old_waiting_room_object,
        stocks_involved=True,
        adding_stock_to_waiting_room=False,
        stock_weight=stock_object.weight,
    )
    session.add(old_waiting_room_object)
    old_waiting_room_id = old_waiting_room_object.id
    stock_object.waiting_room_id = None
    return old_waiting_room_object


async def add_single_stock_to_waiting_room(
    session: AsyncSession,
    waiting_room_id: str,
    stock_schema: StockWaitingRoomInputSchema,
    user_id: str,
) -> dict[str, str]:
    from src.apps.stocks.services.stock_services import (
        manage_resources_state_when_managing_stocks,
    )
    from src.apps.stocks.services.user_stock_services import create_user_stock_object

    if not (
        waiting_room_object := await if_exists(
            WaitingRoom, "id", waiting_room_id, session
        )
    ):
        raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)

    stock_id = stock_schema.id
    if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
        raise DoesNotExist(Stock.__name__, "id", stock_id)

    if stock_object.is_issued:
        raise CannotMoveIssuedStockException

    if stock_object.waiting_room_id == waiting_room_id:
        raise StockAlreadyInWaitingRoomException

    if not waiting_room_object.available_slots:
        raise NoAvailableSlotsInWaitingRoomException

    if waiting_room_object.available_stock_weight < stock_object.weight:
        raise NoAvailableWeightInWaitingRoomException

    _old_waiting_room_id = None
    _old_rack_level_slot_id = None

    if old_waiting_room_object := stock_object.waiting_room:
        old_waiting_room_object = await manage_old_waiting_room_state(
            session,
            stock_object,
            old_waiting_room_object,
            old_waiting_room_id=_old_waiting_room_id,
        )
        _old_waiting_room_id = old_waiting_room_object.id

    if old_rack_level_slot_object := stock_object.rack_level_slot:
        old_rack_level_slot_object = await manage_old_rack_level_slot_state(
            session,
            stock_object,
            old_rack_level_slot_object,
            old_rack_level_slot_id=_old_rack_level_slot_id,
        )
        old_rack_level_slot_object.stock_id = None
        _old_rack_level_slot_id = old_rack_level_slot_object.id

    await create_user_stock_object(
        session,
        stock_object.id,
        user_id,
        from_waiting_room_id=_old_waiting_room_id,
        to_waiting_room_id=waiting_room_object.id,
        from_rack_level_slot_id=_old_rack_level_slot_id,
    )

    waiting_room_object = await manage_waiting_room_state(
        waiting_room_object, stocks_involved=True, stock_weight=stock_object.weight
    )
    session.add(waiting_room_object)

    stock_object.waiting_room_id = waiting_room_object.id
    session.add(stock_object)
    await session.commit()

    return {"message": "Stock was successfully added to the waiting room! "}
