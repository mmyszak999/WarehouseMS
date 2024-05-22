import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.category_schemas import CategoryOutputSchema
from src.apps.products.services.category_services import (
    create_category,
    delete_single_category,
    get_all_categories,
    get_single_category,
    update_single_category,
)
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from src.core.factory.category_factory import CategoryInputSchemaFactory, CategoryUpdateSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import DB_CATEGORY_SCHEMAS, db_categories


@pytest.mark.asyncio
async def test_raise_exception_when_creating_category_that_already_exists(
    async_session: AsyncSession, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(AlreadyExists):
        await create_category(async_session, DB_CATEGORY_SCHEMAS[0])


@pytest.mark.asyncio
async def test_if_only_one_category_was_returned(
    async_session: AsyncSession, db_categories: list[CategoryOutputSchema]
):
    category = await get_single_category(async_session, db_categories.results[1].id)

    assert category.id == db_categories.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_category(
    async_session: AsyncSession, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await get_single_category(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_categories_were_returned(
    async_session: AsyncSession, db_categories: list[CategoryOutputSchema]
):
    categories = await get_all_categories(async_session, PageParams(page=1, size=5))
    assert categories.total == db_categories.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_category(
    async_session: AsyncSession, db_categories: list[CategoryOutputSchema]
):
    update_data = CategoryUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_category(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_if_category_can_have_occupied_name(
    async_session: AsyncSession, db_categories: list[CategoryOutputSchema]
):
    category_data = CategoryInputSchemaFactory().generate(
        name=DB_CATEGORY_SCHEMAS[0].name
    )
    with pytest.raises(IsOccupied):
        await update_single_category(async_session, category_data, db_categories.results[1].id)


@pytest.mark.asyncio
async def test_raise_exception_while_deleting_nonexistent_category(
    async_session: AsyncSession, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await delete_single_category(async_session, generate_uuid())