import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.stocks.schemas.stock_schemas import (
    StockOutputSchema,
    StockWaitingRoomInputSchema,
)
from src.apps.stocks.models import Stock
from src.apps.rack_level_slots.models import RackLevelSlot
from src.apps.stocks.services.stock_services import create_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.schemas import (
    WaitingRoomInputSchema,
    WaitingRoomOutputSchema,
    WaitingRoomUpdateSchema,
)
from src.apps.waiting_rooms.services import (
    add_single_stock_to_waiting_room,
    create_waiting_room,
    delete_single_waiting_room,
    get_all_waiting_rooms,
    get_single_waiting_room,
    manage_waiting_room_state,
    update_single_waiting_room,
    manage_old_waiting_room_state
)
from src.apps.warehouse.services import create_warehouse
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
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.factory.waiting_room_factory import (
    WaitingRoomInputSchemaFactory,
    WaitingRoomUpdateSchemaFactory,
)
from src.core.factory.warehouse_factory import WarehouseInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import db_categories, db_products
from tests.test_sections.conftest import db_sections
from tests.test_rack_levels.conftest import db_rack_levels
from tests.test_racks.conftest import db_racks
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from tests.test_warehouse.conftest import db_warehouse


@pytest.mark.asyncio
async def test_raise_exception_when_creating_waiting_room_with_no_warehouse_created_previously(
    async_session: AsyncSession,
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate()
    with pytest.raises(WarehouseDoesNotExistException):
        await create_waiting_room(async_session, waiting_room_input)


@pytest.mark.asyncio
async def test_raise_exception_when_there_is_no_more_available_waiting_room_when_creating_one(
    async_session: AsyncSession,
):
    warehouse_input = WarehouseInputSchemaFactory().generate(max_waiting_rooms=1)
    warehouse = await create_warehouse(async_session, warehouse_input)

    waiting_room_input_1 = WaitingRoomInputSchemaFactory().generate()
    waiting_room_1 = await create_waiting_room(async_session, waiting_room_input_1)

    waiting_room_input_2 = WaitingRoomInputSchemaFactory().generate()

    with pytest.raises(NotEnoughWarehouseResourcesException):
        await create_waiting_room(async_session, waiting_room_input_2)


@pytest.mark.asyncio
async def test_if_only_one_waiting_room_was_returned(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room = await get_single_waiting_room(
        async_session, db_waiting_rooms.results[1].id
    )

    assert waiting_room.id == db_waiting_rooms.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_waiting_room(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_waiting_room(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_waiting_rooms_were_returned(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_rooms = await get_all_waiting_rooms(
        async_session, PageParams(page=1, size=5)
    )
    assert waiting_rooms.total == waiting_rooms.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_waiitng_room(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    update_data = WaitingRoomInputSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_waiting_room(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_requested_max_weight_is_smaller_than_the_current_stock_weight(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input_1 = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room_1 = await create_waiting_room(
        async_session, waiting_room_input_1, testing=True
    )

    product_count = 5
    stock_input = StockInputSchemaFactory().generate(
        product_weight=db_products.results[0].weight,
        product_count=product_count,
        product_id=db_products.results[0].id,
    )

    stocks = await create_stocks(
        async_session,
        db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[None],
        rack_level_slots_ids=[None],
        testing=True,
        input_schemas=[stock_input],
    )

    stock_schemas = [StockWaitingRoomInputSchema(id=stock.id) for stock in stocks]
    [
        await add_single_stock_to_waiting_room(
            async_session, waiting_room_1.id, stock_schema, db_staff_user.id
        )
        for stock_schema in stock_schemas
    ]

    update_data = WaitingRoomUpdateSchemaFactory().generate(
        max_weight=stocks[0].weight - 1
    )
    with pytest.raises(TooLittleWaitingRoomWeightException):
        await update_single_waiting_room(async_session, update_data, waiting_room_1.id)


@pytest.mark.asyncio
async def test_raise_exception_while_requested_max_stock_amount_is_smaller_than_the_current_stock_amount(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input_1 = WaitingRoomInputSchemaFactory().generate(max_stocks=3)
    waiting_room_1 = await create_waiting_room(
        async_session, waiting_room_input_1, testing=True
    )

    product_count = 5
    stock_inputs = [
        StockInputSchemaFactory().generate(
            product_weight=product.weight,
            product_count=product_count,
            product_id=product.id,
        )
        for product in db_products.results
    ]

    stocks = await create_stocks(
        async_session,
        db_staff_user.id,
        waiting_rooms_ids=[None, None, None],
        rack_level_ids=[None, None, None],
        rack_level_slots_ids=[None, None, None],
        testing=True,
        input_schemas=stock_inputs,
    )

    stock_schemas = [StockWaitingRoomInputSchema(id=stock.id) for stock in stocks]
    [
        await add_single_stock_to_waiting_room(
            async_session, waiting_room_1.id, stock_schema, db_staff_user.id
        )
        for stock_schema in stock_schemas
    ]

    update_data = WaitingRoomUpdateSchemaFactory().generate(max_stocks=1)
    with pytest.raises(TooLittleWaitingRoomSpaceException):
        await update_single_waiting_room(async_session, update_data, waiting_room_1.id)


@pytest.mark.asyncio
async def test_raise_exception_while_deleting_nonexistent_waiitng_room(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await delete_single_waiting_room(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_deleting_waiting_room_with_stocks_inside(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room = await create_waiting_room(async_session, waiting_room_input)
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room.id, stock_schema, db_staff_user.id
    )
    waiting_room = await get_single_waiting_room(async_session, waiting_room.id)

    with pytest.raises(WaitingRoomIsNotEmptyException):
        await delete_single_waiting_room(async_session, waiting_room.id)


@pytest.mark.asyncio
async def test_raise_exception_while_adding_stock_to_nonexistent_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_staff_user: UserOutputSchema,
):
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[1].id)

    with pytest.raises(DoesNotExist):
        await add_single_stock_to_waiting_room(
            async_session, generate_uuid(), stock_schema, db_staff_user.id
        )


@pytest.mark.asyncio
async def test_raise_exception_while_adding_nonexistent_stock_to_waiting_room(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_staff_user: UserOutputSchema,
):
    stock_schema = StockWaitingRoomInputSchema(id=generate_uuid())

    with pytest.raises(DoesNotExist):
        await add_single_stock_to_waiting_room(
            async_session,
            db_waiting_rooms.results[0].id,
            stock_schema,
            db_staff_user.id,
        )


@pytest.mark.asyncio
async def test_raise_exception_while_adding_issued_stock_to_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_staff_user: UserOutputSchema,
):
    issued_stocks = [stock for stock in db_stocks.results if stock.is_issued]
    stock_schema = StockWaitingRoomInputSchema(id=issued_stocks[0].id)

    with pytest.raises(CannotMoveIssuedStockException):
        await add_single_stock_to_waiting_room(
            async_session,
            db_waiting_rooms.results[0].id,
            stock_schema,
            db_staff_user.id,
        )


@pytest.mark.asyncio
async def test_raise_exception_while_adding_stock_to_the_current_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    available_stocks = [stock for stock in db_stocks.results if stock.waiting_room_id]
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)

    with pytest.raises(StockAlreadyInWaitingRoomException):
        await add_single_stock_to_waiting_room(
            async_session,
            available_stocks[0].waiting_room.id,
            stock_schema,
            db_staff_user.id,
        )


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_space_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]

    waiting_room_input = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room = await create_waiting_room(async_session, waiting_room_input)
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room.id, stock_schema, db_staff_user.id
    )

    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[1].id)

    with pytest.raises(NoAvailableSlotsInWaitingRoomException):
        await add_single_stock_to_waiting_room(
            async_session, waiting_room.id, stock_schema, db_staff_user.id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_weight_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_weight=available_stocks[0].weight - 1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input)

    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    with pytest.raises(NoAvailableWeightInWaitingRoomException):
        await add_single_stock_to_waiting_room(
            async_session, waiting_room.id, stock_schema, db_staff_user.id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_no_stock_provided_while_managing_waiting_room_state(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema]
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_weight=available_stocks[0].weight - 1
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )
    with pytest.raises(ServiceException):
        await manage_waiting_room_state(waiting_room, stocks_involved=True)


@pytest.mark.asyncio
async def test_check_if_available_weight_is_set_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=4, max_weight=11111111
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )

    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]

    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room.id, stock_schema, db_staff_user.id
    )

    new_max_weight = available_stocks[0].weight + 20
    waiting_room = await if_exists(WaitingRoom, "id", waiting_room.id, async_session)
    updated_waiting_room = await manage_waiting_room_state(
        waiting_room, max_weight=new_max_weight
    )
    assert (
        updated_waiting_room.available_stock_weight
        == new_max_weight - waiting_room.current_stock_weight
    )


@pytest.mark.asyncio
async def test_check_if_available_stock_amount_is_set_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )

    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room.id, stock_schema, db_staff_user.id
    )

    new_max_stocks = 2
    waiting_room = await if_exists(WaitingRoom, "id", waiting_room.id, async_session)
    updated_waiting_room = await manage_waiting_room_state(
        waiting_room, max_stocks=new_max_stocks
    )
    assert (
        updated_waiting_room.available_slots
        == new_max_stocks - waiting_room.occupied_slots
    )


@pytest.mark.asyncio
async def test_check_if_old_and_new_waiting_room_state_is_managed_correctly(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input_1 = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room_1 = await create_waiting_room(
        async_session, waiting_room_input_1, testing=True
    )

    product_count = 5
    stock_input = StockInputSchemaFactory().generate(
        product_weight=db_products.results[0].weight,
        product_count=product_count,
        product_id=db_products.results[0].id,
    )

    stocks = await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[None, None, None],
        rack_level_slots_ids=[None, None, None],
        testing=True,
        input_schemas=[stock_input],
    )

    stock_schema = StockWaitingRoomInputSchema(id=stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room_1.id, stock_schema, db_staff_user.id
    )
    await async_session.refresh(stocks[0])

    waiting_room_input_2 = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room_2 = await create_waiting_room(
        async_session, waiting_room_input_2, testing=True
    )

    stock_schema = StockWaitingRoomInputSchema(id=stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room_2.id, stock_schema, db_staff_user.id
    )

    new_waiting_room = await if_exists(
        WaitingRoom, "id", waiting_room_2.id, async_session
    )

    old_waiting_room = await if_exists(
        WaitingRoom, "id", waiting_room_1.id, async_session
    )

    await async_session.refresh(old_waiting_room)

    assert new_waiting_room.occupied_slots == 1
    assert new_waiting_room.current_stock_weight == stocks[0].weight

    assert old_waiting_room.occupied_slots == 0
    assert old_waiting_room.current_stock_weight == 0


@pytest.mark.asyncio
async def test_check_if_stock_from_rack_level_slot_is_added_to_the_waiting_room_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input_1 = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room_1 = await create_waiting_room(
        async_session, waiting_room_input_1, testing=True
    )

    stock = await if_exists(
        Stock, "id", db_stocks.results[0].id, async_session
    )
    print(stock.__dict__, "3")
    
    old_rack_level_slot = await if_exists(
        RackLevelSlot, "id", stock.rack_level_slot_id, async_session
    )
    print(old_rack_level_slot.stock, "1")
    
    stock_schema = StockWaitingRoomInputSchema(id=stock.id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room_1.id, stock_schema, db_staff_user.id
    )
    
    print(old_rack_level_slot.__dict__, "2")
    await async_session.refresh(stock)
    print(stock.__dict__, "3")
    
    
    """await async_session.flush()
    await async_session.refresh(waiting_room_1)
    await async_session.refresh(old_rack_level_slot)
    await async_session.refresh(stock)"""
    

    assert waiting_room_1.occupied_slots == 1
    assert old_rack_level_slot.stock_id == None
    assert stock.rack_level_slot_id == None
    assert stock.waiting_room_id == waiting_room_1.id