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
from src.apps.stocks.services.stock_services import (
    create_stocks,
    get_all_available_stocks,
    get_all_stocks,
    get_single_stock,
    issue_stocks,
)
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.models import WaitingRoom
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
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_waiting_rooms.conftest import db_waiting_rooms


@pytest.mark.asyncio
async def test_if_stocks_were_created_correctly(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
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
        async_session, db_staff_user.id, testing=True, input_schemas=stock_inputs
    )

    assert {product_count} == {stock.product_count for stock in stocks}
    assert {product.id for product in db_products.results} == {
        stock.product_id for stock in stocks
    }


@pytest.mark.asyncio
async def test_raise_exception_when_product_data_is_missing(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(MissingProductDataException):
        await create_stocks(async_session, user_id=db_staff_user.id)


@pytest.mark.asyncio
async def test_raise_exception_when_there_is_no_waiting_room_available_for_new_stocks(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]
    with pytest.raises(NoAvailableWaitingRoomsException):
        await create_stocks(
            async_session,
            user_id=db_staff_user.id,
            products=products,
            product_counts=product_counts,
            waiting_rooms_ids=[None]
        )


@pytest.mark.asyncio
async def test_check_if_new_stock_will_be_correctly_added_to_available_waiting_room(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=5, max_weight=9000
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )
    await async_session.flush()

    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]
    stocks = await create_stocks(
        async_session, db_staff_user.id, products, product_counts, waiting_rooms_ids=[waiting_room.id]
    )
    await async_session.flush()
    
    assert stocks[0].waiting_room_id == waiting_room.id
    assert waiting_room.current_stock_weight == stocks[0].weight
    assert waiting_room.occupied_slots == 1


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_stock(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await get_single_stock(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_getting_issued_stock(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    issued_stocks = [stock for stock in db_stocks.results if stock.is_issued]
    with pytest.raises(CannotRetrieveIssuedStockException):
        await get_single_stock(async_session, issued_stocks[0].id)


@pytest.mark.asyncio
async def test_if_all_available_stocks_were_returned(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    stocks = await get_all_available_stocks(async_session, PageParams(page=1, size=5))
    assert stocks.total == db_stocks.total - 1


@pytest.mark.asyncio
async def test_if_all_stocks_were_returned(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    stocks = await get_all_stocks(async_session, PageParams(page=1, size=5))
    assert stocks.total == db_stocks.total


@pytest.mark.asyncio
async def test_if_stocks_are_issued_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    stock_object = await if_exists(Stock, "id", available_stocks[0].id, async_session)
    old_waiting_room = await if_exists(
        WaitingRoom, "id", stock_object.waiting_room_id, async_session
    )
    issue_schema = IssueInputSchemaFactory().generate(
        stock_ids=[StockIssueInputSchema(id=stock_object.id)]
    )
    issue = await create_issue(async_session, issue_schema, db_staff_user.id)
    await async_session.refresh(stock_object)
    await async_session.refresh(old_waiting_room)

    assert {stock.id for stock in issue.stocks} == {stock_object.id}
    assert stock_object.waiting_room == None
    assert old_waiting_room.stocks == []
    assert old_waiting_room.occupied_slots == 0
