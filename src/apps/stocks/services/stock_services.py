from typing import Union
from decimal import Decimal

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.models import Product
from src.apps.stocks.models import Stock, UserStock
from src.apps.stocks.schemas.stock_schemas import (
    StockBasicOutputSchema,
    StockInputSchema,
    StockOutputSchema,
)
from src.apps.stocks.services.user_stock_services import create_user_stock_object
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.services import manage_waiting_room_state
from src.apps.rack_levels.models import RackLevel
from src.apps.rack_level_slots.models import RackLevelSlot
from src.apps.rack_levels.services import manage_rack_level_state
from src.apps.sections.services import manage_section_state
from src.apps.racks.services import manage_rack_state
from src.core.exceptions import (
    AlreadyExists,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    MissingProductDataException,
    NoAvailableWaitingRoomsException,
    ServiceException,
    NotEnoughRackLevelResourcesException,
    NoAvailableRackLevelSlotException,
    AmbiguousStockStoragePlaceDuringReceptionException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists
from src.core.utils.time import get_current_time


async def create_stocks(
    session: AsyncSession,
    user_id: str,
    waiting_rooms_ids: list[str],
    rack_level_slots_ids: list[str],
    rack_level_ids: list[str],
    products: list[Product] = [],
    product_counts: list[int] = [],
    reception_id: str = None,
    testing: bool = False,
    input_schemas: list[StockInputSchema] = None,
) -> list[Stock]:
    stock_list = []
    if testing and input_schemas:
        for schema in input_schemas:
            new_stock = Stock(**schema.dict())
            session.add(new_stock)
            stock_list.append(new_stock)
        await session.commit()
        return stock_list

    if not (products or product_counts):
        raise MissingProductDataException

    _rack_level_slot_id = None
    _waiting_room_id = None
    _rack_level_slot = None
    
    for product, product_count, waiting_room_id, rack_level_slot_id, rack_level_id in zip(
        products, product_counts, waiting_rooms_ids, rack_level_slots_ids, rack_level_ids
    ):
        entered_values_check = [waiting_room_id, rack_level_slot_id, rack_level_id].count(None)
        print(entered_values_check)
        if entered_values_check < 2: 
            raise AmbiguousStockStoragePlaceDuringReceptionException
        
        stock_weight = product_count * product.weight
        statement = select(WaitingRoom).filter(
            WaitingRoom.available_slots >= 1,
            WaitingRoom.available_stock_weight >= stock_weight,
        )
        
        stock_input = StockInputSchema(
            weight=stock_weight,
            product_count=product_count,
            product_id=product.id,
            reception_id=reception_id
        )
        
        if entered_values_check == 3:
            statement = statement.limit(1)
            available_waiting_room = await session.execute(statement)
            waiting_room = available_waiting_room.scalar()
            if not waiting_room:
                raise NoAvailableWaitingRoomsException(
                    product.name, product_count, stock_weight
                )
            stock_input.waiting_room_id = waiting_room.id
            waiting_room = await manage_waiting_room_state(
            waiting_room, stocks_involved=True, stock_weight=stock_weight
            )
            session.add(waiting_room)
            
            _waiting_room_id = waiting_room.id
            
        if waiting_room_id is not None:
            if not (await if_exists(WaitingRoom, "id", waiting_room_id, session)):
                raise DoesNotExist(WaitingRoom.__name__, "id", waiting_room_id)
            statement = statement.where(WaitingRoom.id.in_([waiting_room_id])).limit(1)
            waiting_room = await session.execute(statement)
            waiting_room = waiting_room.scalar()
            if not waiting_room:
                raise NoAvailableWaitingRoomsException(
                    product.name, product_count, stock_weight
                )
            stock_input.waiting_room_id = waiting_room.id
            waiting_room = await manage_waiting_room_state(
            waiting_room, stocks_involved=True, stock_weight=stock_weight
            )
            session.add(waiting_room)
            _waiting_room_id = waiting_room_id
        
        if rack_level_slot_id is not None:
            if not (rack_level_slot_object := await if_exists(RackLevelSlot, "id", rack_level_slot_id, session)):
                raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)
            
            if rack_level_slot_object.stock or (not rack_level_slot_object.is_active):
                raise ServiceException("Requested rack level slot is occupied or inactive")
            
            rack_level_object = rack_level_slot_object.rack_level
            
            if rack_level_object.available_weight < stock_weight:
                raise NotEnoughRackLevelResourcesException(
                    resource="weight", reason="Amount of available weight too low for a new stock! "
                )
            stock_input.rack_level_slot_id = rack_level_slot_object.id
            await manage_resources_state_when_managing_stocks(
                session, rack_level_slot_object, stock_weight, adding_resources=False
            )
            
            _rack_level_slot_id = rack_level_slot_id
            _rack_level_slot = rack_level_slot_object
            
            
        if rack_level_id is not None:
            if not (rack_level_object := await if_exists(RackLevel, "id", rack_level_id, session)):
                raise DoesNotExist(RackLevel.__name__, "id", rack_level_id)
            
            if not rack_level_object.available_slots:
                raise NotEnoughRackLevelResourcesException(
                    resource="slots", reason="No available slots for a new stock! "
                )
            
            if rack_level_object.available_weight < stock_weight:
                raise NotEnoughRackLevelResourcesException(
                    resource="weight", reason="Amount of available weight too low for a new stock! "
                )
            
            statement = select(RackLevelSlot).filter(
            RackLevelSlot.stock == None,
            RackLevelSlot.is_active == True
            ).order_by(RackLevelSlot.rack_level_slot_number.asc()).limit(1)
            
            available_rack_level_slot = await session.execute(statement)
            rack_level_slot_object = available_rack_level_slot.scalar()
            if not rack_level_slot_object:
                raise NoAvailableRackLevelSlotException(
                    product.name, product_count, stock_weight
                )
            stock_input.rack_level_slot_id = rack_level_slot_object.id
            await manage_resources_state_when_managing_stocks(
                session, rack_level_slot_object, stock_weight, adding_resources=False
            )
            
            _rack_level_slot_id = rack_level_slot_object.id
            _rack_level_slot = rack_level_slot_object
        
        print("wow", stock_input.dict())
        new_stock = Stock(**stock_input.dict())
        session.add(new_stock)
        await session.flush()
        
        await create_user_stock_object(
            session, new_stock.id, user_id, to_rack_level_slot_id=_rack_level_slot_id,
            to_waiting_room_id=_waiting_room_id
            )
        stock_list.append(new_stock)
        
        if _rack_level_slot:
            _rack_level_slot.stock_id = new_stock.id
            session.add(_rack_level_slot)
        
        await session.flush()
        print(_rack_level_slot.__dict__)
    return stock_list


async def get_single_stock(
    session: AsyncSession, stock_id: int, can_get_issued: bool = False
) -> StockOutputSchema:
    if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
        raise DoesNotExist(Stock.__name__, "id", stock_id)

    if (not can_get_issued) and stock_object.is_issued:
        raise CannotRetrieveIssuedStockException
    return StockOutputSchema.from_orm(stock_object)


async def get_multiple_stocks(
    session: AsyncSession,
    page_params: PageParams,
    schema: BaseModel = StockBasicOutputSchema,
    get_issued: bool = False,
) -> Union[
    PagedResponseSchema[StockBasicOutputSchema],
    PagedResponseSchema[StockOutputSchema],
]:
    query = select(Stock)
    if not get_issued:
        query = query.filter(Stock.is_issued == False)

    return await paginate(
        query=query,
        response_schema=schema,
        table=Stock,
        page_params=page_params,
        session=session,
    )


async def get_all_stocks(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[StockOutputSchema]:
    return await get_multiple_stocks(
        session, page_params, schema=StockOutputSchema, get_issued=True
    )


async def get_all_available_stocks(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[StockBasicOutputSchema]:
    return await get_multiple_stocks(session, page_params)


async def issue_stocks(
    session: AsyncSession, stocks: list[Stock], issue_id: str, user_id: str
) -> list[Stock]:
    for stock in stocks:
        if stock.waiting_room:
            stock_waiting_room = await if_exists(
                WaitingRoom, "id", stock.waiting_room_id, session
            )
            stock_waiting_room = await manage_waiting_room_state(
                waiting_room_object=stock_waiting_room,
                stocks_involved=True,
                adding_stock_to_waiting_room=False,
                stock_weight=stock.weight,
            )
            session.add(stock_waiting_room)
            user_stock_object = await create_user_stock_object(
                session,
                stock.id,
                user_id,
                from_waiting_room_id=stock_waiting_room.id,
                issue_id=issue_id,
            )
            stock.issue_id = issue_id
            stock.is_issued = True
            stock.updated_at = get_current_time()
            stock.waiting_room_id = None
            stock.waiting_room = None
            session.add(stock)
    return stocks


async def manage_resources_state_when_managing_stocks(
    session: AsyncSession,
    rack_level_slot_object: RackLevelSlot, stock_weight: Decimal,
    adding_resources: bool = True
) -> None:
    rack_level_object = await manage_rack_level_state(
            rack_level_slot_object.rack_level, adding_resources_to_rack_level=adding_resources, slots_involved=True,
            weight_involved=True, stock_weight=stock_weight
        )
    session.add(rack_level_object)
    print(rack_level_object.__dict__)
            
    rack_object = await manage_rack_state(
        rack_level_object.rack, adding_resources_to_rack=adding_resources,
        weight_involved=True, stock_weight=stock_weight
    )
    session.add(rack_object)
    print(rack_object.__dict__)
            
    section_object = await manage_section_state(
        rack_object.section, adding_resources_to_section=adding_resources,
        weight_involved=True, stock_weight=stock_weight
    )
    session.add(section_object)
    print(section_object.__dict__)
    session.add(rack_level_slot_object)
