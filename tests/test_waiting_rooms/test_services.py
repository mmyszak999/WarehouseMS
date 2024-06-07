import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.schemas import IssueOutputSchema
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.stocks.schemas import StockOutputSchema, StockWaitingRoomInputSchema
from src.apps.stocks.services import create_stocks
from src.apps.users.schemas import UserOutputSchema
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
)
from src.core.exceptions import (
    AlreadyExists,
    CannotMoveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    NoAvailableSlotsInWaitingRoomException,
    NoAvailableWeightInWaitingRoomException,
    ServiceException,
    StockAlreadyInWaitingRoomException,
    TooLittleWaitingRoomSpaceException,
    TooLittleWaitingRoomWeightException,
    WaitingRoomIsNotEmptyException,
)
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.factory.waiting_room_factory import (
    WaitingRoomInputSchemaFactory,
    WaitingRoomUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_issues.conftest import db_issues
from tests.test_products.conftest import db_categories, db_products
from tests.test_receptions.conftest import db_receptions
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_waiting_rooms.conftest import db_waiting_rooms


@pytest.mark.asyncio
async def test_if_only_one_waiting_room_was_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room = await get_single_waiting_room(
        async_session, db_waiting_rooms.results[1].id
    )

    assert waiting_room.id == db_waiting_rooms.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_waiting_room(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_waiting_rooms_were_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_rooms = await get_all_waiting_rooms(
        async_session, PageParams(page=1, size=5)
    )
    assert waiting_rooms.total == waiting_rooms.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_waiitng_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    update_data = WaitingRoomInputSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_waiting_room(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_requested_max_weight_is_smaller_than_the_current_stock_weight(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
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
        async_session, testing=True, input_schemas=[stock_input]
    )

    stock_schemas = [StockWaitingRoomInputSchema(id=stock.id) for stock in stocks]
    [
        await add_single_stock_to_waiting_room(
            async_session, waiting_room_1.id, stock_schema
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
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
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
        async_session, testing=True, input_schemas=stock_inputs
    )

    stock_schemas = [StockWaitingRoomInputSchema(id=stock.id) for stock in stocks]
    [
        await add_single_stock_to_waiting_room(
            async_session, waiting_room_1.id, stock_schema
        )
        for stock_schema in stock_schemas
    ]

    update_data = WaitingRoomUpdateSchemaFactory().generate(max_stocks=1)
    with pytest.raises(TooLittleWaitingRoomSpaceException):
        await update_single_waiting_room(async_session, update_data, waiting_room_1.id)


@pytest.mark.asyncio
async def test_raise_exception_while_deleting_nonexistent_waiitng_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await delete_single_waiting_room(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_deleting_waiting_room_with_stocks_inside(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room = await create_waiting_room(async_session, waiting_room_input)
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)
    waiting_room = await get_single_waiting_room(async_session, waiting_room.id)

    with pytest.raises(WaitingRoomIsNotEmptyException):
        await delete_single_waiting_room(async_session, waiting_room.id)


@pytest.mark.asyncio
async def test_raise_exception_while_adding_stock_to_nonexistent_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[1].id)

    with pytest.raises(DoesNotExist):
        await add_single_stock_to_waiting_room(
            async_session, generate_uuid(), stock_schema
        )


@pytest.mark.asyncio
async def test_raise_exception_while_adding_nonexistent_stock_to_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    stock_schema = StockWaitingRoomInputSchema(id=generate_uuid())

    with pytest.raises(DoesNotExist):
        await add_single_stock_to_waiting_room(
            async_session, db_waiting_rooms.results[0].id, stock_schema
        )


@pytest.mark.asyncio
async def test_raise_exception_while_adding_issued_stock_to_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    issued_stocks = [stock for stock in db_stocks.results if stock.is_issued]
    stock_schema = StockWaitingRoomInputSchema(id=issued_stocks[0].id)

    with pytest.raises(CannotMoveIssuedStockException):
        await add_single_stock_to_waiting_room(
            async_session, db_waiting_rooms.results[0].id, stock_schema
        )


@pytest.mark.asyncio
async def test_raise_exception_while_adding_stock_to_the_current_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)

    with pytest.raises(StockAlreadyInWaitingRoomException):
        await add_single_stock_to_waiting_room(
            async_session, available_stocks[0].waiting_room.id, stock_schema
        )


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_space_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]

    waiting_room_input = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room = await create_waiting_room(async_session, waiting_room_input)
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)

    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[1].id)

    with pytest.raises(NoAvailableSlotsInWaitingRoomException):
        await add_single_stock_to_waiting_room(
            async_session, waiting_room.id, stock_schema
        )


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_weight_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_weight=available_stocks[0].weight - 1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input)

    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    with pytest.raises(NoAvailableWeightInWaitingRoomException):
        await add_single_stock_to_waiting_room(
            async_session, waiting_room.id, stock_schema
        )


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_weight_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_weight=available_stocks[0].weight - 1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input)

    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    with pytest.raises(NoAvailableWeightInWaitingRoomException):
        await add_single_stock_to_waiting_room(
            async_session, waiting_room.id, stock_schema
        )


@pytest.mark.asyncio
async def test_raise_exception_when_no_stock_provided_while_managing_waiting_room_state(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
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
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=4, max_weight=11111111
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )

    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]

    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)

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
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )

    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    stock_schema = StockWaitingRoomInputSchema(id=available_stocks[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)

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
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
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
        async_session, testing=True, input_schemas=[stock_input]
    )

    stock_schema = StockWaitingRoomInputSchema(id=stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room_1.id, stock_schema
    )
    await async_session.refresh(stocks[0])

    waiting_room_input_2 = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room_2 = await create_waiting_room(
        async_session, waiting_room_input_2, testing=True
    )

    stock_schema = StockWaitingRoomInputSchema(id=stocks[0].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room_2.id, stock_schema
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
