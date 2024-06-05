import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.waiting_rooms.schemas import (
    WaitingRoomInputSchema, WaitingRoomOutputSchema, WaitingRoomUpdateSchema
)
from src.apps.waiting_rooms.services import (
    create_waiting_room,
    get_all_waiting_rooms,
    get_single_waiting_room,
    update_single_waiting_room,
    delete_single_waiting_room,
    add_single_stock_to_waiting_room,
    manage_waiting_room_state
)
from src.apps.users.schemas import UserOutputSchema
from src.apps.stocks.schemas import StockOutputSchema, StockWaitingRoomInputSchema
from src.apps.issues.schemas import IssueOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.waiting_rooms.models import WaitingRoom
from src.core.utils.orm import if_exists
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    TooLittleWaitingRoomWeightException,
    ServiceException,
    TooLittleWaitingRoomSpaceException,
    WaitingRoomIsNotEmptyException,
    CannotMoveIssuedStockException,
    StockAlreadyInWaitingRoomException,
    NoAvailableSlotsInWaitingRoomException,
    NoAvailableWeightInWaitingRoomException,
    ServiceException
)
from src.core.factory.waiting_room_factory import (
    WaitingRoomUpdateSchemaFactory,
    WaitingRoomInputSchemaFactory
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_issues.conftest import db_issues
from tests.test_products.conftest import db_products, db_categories
from tests.test_receptions.conftest import db_receptions
from tests.test_stocks.conftest import db_stocks
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from src.core.utils.utils import generate_uuid
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_if_only_one_waiting_room_was_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room = await get_single_waiting_room(async_session, db_waiting_rooms.results[1].id)

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
    waiting_rooms = await get_all_waiting_rooms(async_session, PageParams(page=1, size=5))
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
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    waiting_room = db_waiting_rooms.results[0]
    update_data = WaitingRoomUpdateSchemaFactory().generate(max_weight=0.00001)
    with pytest.raises(TooLittleWaitingRoomWeightException):
        await update_single_waiting_room(async_session, update_data, waiting_room.id)


@pytest.mark.asyncio
async def test_raise_exception_while_requested_max_stock_amount_is_smaller_than_the_current_stock_amount(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    waiting_room = db_waiting_rooms.results[0]
    
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[1].id)
    await add_single_stock_to_waiting_room(
        async_session, waiting_room.id, stock_schema
    )
    
    update_data = WaitingRoomUpdateSchemaFactory().generate(max_stocks=1)
    with pytest.raises(TooLittleWaitingRoomSpaceException):
        await update_single_waiting_room(async_session, update_data, waiting_room.id)



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
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
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
        await add_single_stock_to_waiting_room(async_session, generate_uuid(), stock_schema)


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
        await add_single_stock_to_waiting_room(async_session, db_waiting_rooms.results[0].id, stock_schema)


@pytest.mark.asyncio
async def test_raise_exception_while_adding_issued_stock_to_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[2].id)

    with pytest.raises(CannotMoveIssuedStockException):
        await add_single_stock_to_waiting_room(async_session, db_waiting_rooms.results[0].id, stock_schema)


@pytest.mark.asyncio
async def test_raise_exception_while_adding_stock_to_the_current_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)

    with pytest.raises(StockAlreadyInWaitingRoomException):
        await add_single_stock_to_waiting_room(async_session, db_waiting_rooms.results[0].id, stock_schema)


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_space_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(max_stocks=1)
    waiting_room = await create_waiting_room(async_session, waiting_room_input)
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)
    
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[1].id)

    with pytest.raises(NoAvailableSlotsInWaitingRoomException):
        await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_weight_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_weight=db_stocks.results[0].weight - 1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input)
    
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
    with pytest.raises(NoAvailableWeightInWaitingRoomException):
        await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_got_no_available_weight_for_new_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_weight=db_stocks.results[0].weight - 1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input)
    
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
    with pytest.raises(NoAvailableWeightInWaitingRoomException):
        await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)


@pytest.mark.asyncio
async def test_raise_exception_when_no_stock_provided_when_managing_waiting_room_state(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_weight=db_stocks.results[0].weight - 1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input, testing=True)
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
        max_stocks=4,
        max_weight=db_stocks.results[0].weight
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input, testing=True)
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)
    
    new_max_weight = db_stocks.results[0].weight+20
    waiting_room = await if_exists(
            WaitingRoom, "id", waiting_room.id, async_session
    )
    updated_waiting_room = await manage_waiting_room_state(waiting_room, max_weight=new_max_weight)
    assert updated_waiting_room.available_stock_weight == new_max_weight - waiting_room.current_stock_weight


@pytest.mark.asyncio
async def test_check_if_available_stock_amount_is_set_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input, testing=True)
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)
    
    new_max_stocks = 2
    waiting_room = await if_exists(
            WaitingRoom, "id", waiting_room.id, async_session
    )
    updated_waiting_room = await manage_waiting_room_state(waiting_room, max_stocks=new_max_stocks)
    assert updated_waiting_room.available_slots == new_max_stocks - waiting_room.occupied_slots


@pytest.mark.asyncio
async def test_check_if_old_waiting_room_state_is_managed_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=1
    )
    waiting_room = await create_waiting_room(async_session, waiting_room_input, testing=True)
    stock = db_stocks.results[0]
    old_waiting_room = stock.waiting_room
    
    stock_schema = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
    await add_single_stock_to_waiting_room(async_session, waiting_room.id, stock_schema)
    waiting_room = await if_exists(
            WaitingRoom, "id", waiting_room.id, async_session
    )
    assert waiting_room.occupied_slots == 1
    assert waiting_room.current_stock_weight == stock.weight
    
    old_waiting_room = await if_exists(
            WaitingRoom, "id", old_waiting_room.id, async_session
    )
    
    assert old_waiting_room.occupied_slots == 0
    assert old_waiting_room.current_stock_weight == 0    







