import pytest
from sqlalchemy.ext.asyncio import AsyncSession


from src.apps.receptions.services import (
    base_create_reception,
    get_single_reception,
    get_all_receptions,
    update_single_reception
)
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.core.factory.reception_factory import (
    ReceptionInputSchemaFactory,
    ReceptionProductInputSchemaFactory,
    ReceptionUpdateSchemaFactory
)
from src.core.pagination.schemas import PagedResponseSchema
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from tests.test_stocks.conftest import db_stocks
from tests.test_receptions.conftest import db_receptions
from tests.test_issues.conftest import db_issues
from tests.test_products.conftest import db_products
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid


@pytest.mark.asyncio
async def test_if_reception_was_created_correctly(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema
):
    reception_input = ReceptionInputSchemaFactory().generate(
        products_data=[ReceptionProductInputSchemaFactory().generate(
            db_products.results[0].id, product_count=5
        )], description="descr"
    )
    reception = await base_create_reception(async_session, reception_input, db_staff_user.id, testing=True)
    
    assert reception.user_id == db_staff_user.id
    assert reception.description == reception_input.description


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
    