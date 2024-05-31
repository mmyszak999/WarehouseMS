import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.schemas import IssueOutputSchema
from src.apps.issues.services import base_create_issue
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.stocks.services import (
    create_stocks,
    get_all_available_stocks,
    get_all_stocks,
    get_single_stock,
    issue_stocks,
)
from src.apps.users.schemas import UserOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    MissingProductDataException,
)
from src.core.factory.issue_factory import IssueInputSchemaFactory
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_issues.conftest import db_issues
from tests.test_products.conftest import db_products
from tests.test_receptions.conftest import db_receptions
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


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
        async_session, testing=True, input_schemas=stock_inputs
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
        await create_stocks(async_session)


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_stock(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_stock(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_getting_issued_stock(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    with pytest.raises(CannotRetrieveIssuedStockException):
        await get_single_stock(async_session, db_stocks.results[2].id)


@pytest.mark.asyncio
async def test_if_all_available_stocks_were_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    stocks = await get_all_available_stocks(async_session, PageParams(page=1, size=5))
    assert stocks.total == db_stocks.total - 1


@pytest.mark.asyncio
async def test_if_all_stocks_were_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    stocks = await get_all_stocks(async_session, PageParams(page=1, size=5))
    assert stocks.total == db_stocks.total


@pytest.mark.asyncio
async def test_if_stocks_are_issued_correctly(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    stock_inputs = [
        StockInputSchemaFactory().generate(
            product_weight=product.weight, product_count=5, product_id=product.id
        )
        for product in db_products.results
    ]

    issue = await base_create_issue(async_session, db_staff_user.id, testing=True)

    stocks = await create_stocks(
        async_session, testing=True, input_schemas=stock_inputs
    )
    issued_stocks = await issue_stocks(async_session, stocks, issue.id)

    assert len(issued_stocks) == len(
        {stock for stock in issued_stocks if stock.is_issued}
    )
    assert {stock.issue_id for stock in issued_stocks} == {issue.id}
