import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.services import create_issue
from src.apps.products.models import Product
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas.stock_schemas import (
    StockIssueInputSchema,
    StockOutputSchema,
)
from src.apps.stocks.schemas.user_stock_schemas import UserStockOutputSchema
from src.apps.stocks.services.user_stock_services import (
    create_user_stock_object,
    get_all_user_stock_history_for_single_stock,
    get_all_user_stocks,
    get_all_user_stocks_with_single_user_involvement,
    get_multiple_user_stocks,
    get_single_user_stock,
)
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.schemas import WaitingRoomOutputSchema
from src.apps.waiting_rooms.services import create_waiting_room
from src.core.exceptions import (
    AlreadyExists,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    MissingProductDataException,
    NoAvailableWaitingRoomsException,
)
from src.core.factory.issue_factory import IssueInputSchemaFactory
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.factory.waiting_room_factory import WaitingRoomInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import db_products
from tests.test_sections.conftest import db_sections
from tests.test_stocks.conftest import db_stocks, db_user_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from tests.test_warehouse.conftest import db_warehouse


@pytest.mark.asyncio
async def test_user_stock_object_is_created_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    user_stock = await create_user_stock_object(
        async_session,
        user_id=db_staff_user.id,
        stock_id=db_stocks.results[0].id,
        from_waiting_room_id=db_waiting_rooms.results[0].id,
        to_waiting_room_id=db_waiting_rooms.results[1].id,
    )

    assert user_stock.user.id == db_staff_user.id
    assert user_stock.stock.id == db_stocks.results[0].id
    assert user_stock.from_waiting_room.id == db_waiting_rooms.results[0].id
    assert user_stock.to_waiting_room.id == db_waiting_rooms.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_when_creating_user_stock_with_nonexistent_waiting_rooms(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await create_user_stock_object(
            async_session,
            from_waiting_room_id=generate_uuid(),
            user_id=db_staff_user.id,
            stock_id=db_stocks.results[0].id,
        )

    with pytest.raises(DoesNotExist):
        await create_user_stock_object(
            async_session,
            to_waiting_room_id=generate_uuid(),
            user_id=db_staff_user.id,
            stock_id=db_stocks.results[0].id,
        )


@pytest.mark.asyncio
async def test_raise_exception_when_creating_user_stock_with_nonexistent_user(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await create_user_stock_object(
            async_session, user_id=generate_uuid(), stock_id=db_stocks.results[0].id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_creating_user_stock_with_nonexistent_stock(
    async_session: AsyncSession,
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await create_user_stock_object(
            async_session, stock_id=generate_uuid(), user_id=db_staff_user.id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_creating_user_stock_with_nonexistent_issue(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await create_user_stock_object(
            async_session,
            issue_id=generate_uuid(),
            user_id=db_staff_user.id,
            stock_id=db_stocks.results[0].id,
        )


@pytest.mark.asyncio
async def test_raise_exception_when_getting_nonexistent_user_stock(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await get_single_user_stock(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_check_if_single_user_stock_was_returned(
    async_session: AsyncSession,
    db_user_stocks: PagedResponseSchema[UserStockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    user_stock = await get_single_user_stock(
        async_session, db_user_stocks.results[0].id
    )
    assert db_user_stocks.results[0].id == user_stock.id
    assert db_user_stocks.results[0].stock.id == user_stock.stock.id


@pytest.mark.asyncio
async def test_check_if_returned_stock_history_is_complete_and_got_only_one_stock_involved(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    issued_stocks = [stock for stock in db_stocks.results if stock.is_issued]
    user_stocks = await get_all_user_stock_history_for_single_stock(
        async_session, PageParams(), stock_id=issued_stocks[0].id
    )

    assert user_stocks.total == 2
    assert {user_stock.stock.id for user_stock in user_stocks.results} == {
        issued_stocks[0].id
    }


@pytest.mark.asyncio
async def test_raise_exception_when_getting_stock_history_for_nonexistent_stock(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await get_all_user_stock_history_for_single_stock(
            async_session, PageParams(), stock_id=generate_uuid()
        )


@pytest.mark.asyncio
async def test_check_if_returned_stock_history_contain_only_single_user_activities(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    user_stocks = await get_all_user_stocks_with_single_user_involvement(
        async_session, PageParams(), user_id=db_staff_user.id
    )

    assert {user_stock.user.id for user_stock in user_stocks.results} == {
        db_staff_user.id
    }


@pytest.mark.asyncio
async def test_raise_exception_when_getting_stock_history_containing_only_single_user_activities(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await get_all_user_stocks_with_single_user_involvement(
            async_session, PageParams(), user_id=generate_uuid()
        )
