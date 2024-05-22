import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.category_schemas import CategoryOutputSchema, CategoryIdListSchema
from src.apps.products.schemas.product_schemas import ProductOutputSchema, RemovedProductOutputSchema
from src.apps.products.services.product_services import (
    create_product,
    get_single_product,
    get_all_available_products,
    get_available_single_product,
    get_all_products,
    get_multiple_products,
    update_single_product,
    make_single_product_legacy
)
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied, ProductIsAlreadyLegacyException
from src.core.factory.category_factory import CategoryInputSchemaFactory, CategoryUpdateSchemaFactory
from src.core.factory.product_factory import ProductInputSchemaFactory, ProductUpdateSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.utils import generate_uuid
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_products.conftest import DB_CATEGORY_SCHEMAS, db_categories, db_products


@pytest.mark.asyncio
async def test_raise_exception_when_other_product_have_the_same_name(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    product_data = ProductInputSchemaFactory().generate(name=db_products.results[0].name)
    with pytest.raises(AlreadyExists):
        await create_product(async_session, product_data)


@pytest.mark.asyncio
async def test_if_only_single_product_was_returned(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    product = await get_single_product(async_session, db_products.results[1].id)

    assert product.id == db_products.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_product(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await get_single_product(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_products_were_returned(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    products = await get_all_products(async_session, PageParams(page=1, size=5))
    assert products.total == db_products.total


@pytest.mark.asyncio
async def test_if_legacy_product_displayed_with_correct_schema(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    product = db_products.results[0]
    await make_single_product_legacy(async_session, product.id)
    
    result = await get_available_single_product(async_session, product.id)
    assert result.legacy_product == True
    assert type(result) == RemovedProductOutputSchema


@pytest.mark.asyncio
async def test_if_product_can_have_occupied_name(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    product_data = ProductUpdateSchemaFactory().generate(name=db_products.results[0].name)
    with pytest.raises(IsOccupied):
        await update_single_product(async_session, product_data, db_products.results[1].id)


@pytest.mark.asyncio
async def test_raise_exception_while_making_nonexistent_product_legacy_one(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await make_single_product_legacy(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_removing_product_from_store_that_is_already_removed(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    product = db_products.results[0]
    await make_single_product_legacy(async_session, product.id)
    
    with pytest.raises(ProductIsAlreadyLegacyException):
        await make_single_product_legacy(async_session, product.id)


@pytest.mark.asyncio
async def test_if_legacy_product_cannot_be_modified(
    async_session: AsyncSession, db_products: PagedResponseSchema[ProductOutputSchema]
):
    product = db_products.results[0]
    await make_single_product_legacy(async_session, product.id)
    
    update_data = ProductUpdateSchemaFactory().generate(name="updated_name")
    with pytest.raises(ProductIsAlreadyLegacyException):
        await make_single_product_legacy(async_session, product.id)


@pytest.mark.asyncio
async def test_if_product_can_be_created_with_no_category_attached(
    async_session: AsyncSession, db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    product_data = ProductInputSchemaFactory().generate()
    product = await create_product(async_session, product_data)

    assert len(product.categories) == 0


@pytest.mark.asyncio
async def test_if_product_can_have_multiple_categories(
    async_session: AsyncSession, db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    product_data = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[
            db_categories.results[0].id, db_categories.results[1].id]
        ),
    )
    product = await create_product(async_session, product_data)

    assert len(product.categories) == 2


@pytest.mark.asyncio
async def test_if_product_can_have_no_categories_after_update(
    async_session: AsyncSession,
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
):
    product_data = ProductUpdateSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[])
        )
    await update_single_product(async_session, product_data, db_products.results[0].id)

    product = await get_single_product(async_session, db_products.results[0].id)
    assert len(product.categories) == 0