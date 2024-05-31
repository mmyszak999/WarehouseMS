import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.receptions.services import (
    base_create_reception,
    get_all_receptions,
    get_single_reception,
    update_single_reception,
)
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    MissingReceptionDataException,
    ServiceException,
)
from src.core.factory.reception_factory import (
    ReceptionInputSchemaFactory,
    ReceptionProductInputSchemaFactory,
    ReceptionUpdateSchemaFactory,
)
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
async def test_if_reception_was_created_correctly(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    reception_input = ReceptionInputSchemaFactory().generate(
        products_data=[
            ReceptionProductInputSchemaFactory().generate(
                db_products.results[0].id, product_count=5
            )
        ],
        description="descr",
    )
    reception = await base_create_reception(
        async_session, db_staff_user.id, reception_input, testing=True
    )

    assert reception.user_id == db_staff_user.id


@pytest.mark.asyncio
async def test_raise_exception_when_products_are_not_consistent_with_their_counts(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    reception_input = ReceptionInputSchemaFactory().generate(
        products_data=[
            ReceptionProductInputSchemaFactory().generate(
                db_products.results[0].id, product_count=5
            ),
            ReceptionProductInputSchemaFactory().generate(
                db_products.results[0].id, product_count=4
            ),
        ],
        description="descr",
    )
    with pytest.raises(ServiceException):
        await base_create_reception(async_session, db_staff_user.id, reception_input)


@pytest.mark.asyncio
async def test_raise_exception_when_reception_data_is_missing(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(MissingReceptionDataException):
        await base_create_reception(async_session, db_staff_user.id)


@pytest.mark.asyncio
async def test_if_only_one_reception_was_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):
    reception = await get_single_reception(async_session, db_receptions.results[1].id)

    assert reception.id == db_receptions.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_reception(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_reception(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_receptions_were_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):
    receptions = await get_all_receptions(async_session, PageParams(page=1, size=5))
    assert receptions.total == db_receptions.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_reception(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):
    update_data = ReceptionUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_reception(async_session, update_data, generate_uuid())
