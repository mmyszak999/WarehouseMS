from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from src.apps.products.models import (
    Category,
    Product,
    category_product_association_table,
)
from src.apps.products.schemas.product_schemas import (
    ProductBasicOutputSchema,
    ProductInputSchema,
    ProductOutputSchema,
    ProductUpdateSchema,
    RemovedProductOutputSchema,
)
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    LegacyProductException,
    ProductIsAlreadyLegacyException,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def create_product(
    session: AsyncSession, product_input: ProductInputSchema
) -> ProductOutputSchema:
    product_data = product_input.dict(exclude_none=True, exclude_unset=True)

    if product_data.get("name"):
        name_check = await session.scalar(
            select(Product).filter(Product.name == product_data["name"]).limit(1)
        )
        if name_check:
            raise AlreadyExists(Product.__name__, "name", product_data["name"])

    if category_ids := product_data.get("category_ids"):
        category_ids = category_ids.get("id")
        categories = await session.scalars(
            select(Category).where(Category.id.in_(category_ids))
        )
        categories = categories.all()
        if not len(set(category_ids)) == len(categories):
            raise ServiceException("Wrong categories!")

        product_data["categories"] = categories
        print(category_ids, "ww")

    if category_ids is not None:
        product_data.pop("category_ids")

    new_product = Product(**product_data)

    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)

    return ProductOutputSchema.from_orm(new_product)


async def get_available_single_product(
    session: AsyncSession, product_id: str
) -> Union[ProductBasicOutputSchema, RemovedProductOutputSchema]:
    if not (product_object := await if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)

    if product_object.legacy_product:
        return RemovedProductOutputSchema.from_orm(product_object)
    return ProductBasicOutputSchema.from_orm(product_object)


async def get_single_product(
    session: AsyncSession, product_id: str
) -> ProductOutputSchema:
    if not (product_object := await if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)

    return ProductOutputSchema.from_orm(product_object)


async def get_multiple_products(
    session: AsyncSession,
    page_params: PageParams,
    schema: BaseModel = ProductBasicOutputSchema,
    get_legacy: bool = False,
    query_params: list[tuple] = None,
) -> Union[
    PagedResponseSchema[ProductBasicOutputSchema],
    PagedResponseSchema[ProductOutputSchema],
]:
    query = select(Product)
    if not get_legacy:
        query = query.filter(Product.legacy_product == False)

    query = query.join(
        category_product_association_table,
        Product.id == category_product_association_table.c.product_id,
        isouter=True,
    ).join(
        Category,
        category_product_association_table.c.category_id == Category.id,
        isouter=True,
    )

    if query_params:
        query = filter_and_sort_instances(query_params, query, Product)

    return await paginate(
        query=query,
        response_schema=schema,
        table=Product,
        page_params=page_params,
        session=session,
    )


async def get_all_products(
    session: AsyncSession, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[ProductOutputSchema]:
    return await get_multiple_products(
        session,
        page_params,
        schema=ProductOutputSchema,
        get_legacy=True,
        query_params=query_params,
    )


async def get_all_available_products(
    session: AsyncSession, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[ProductBasicOutputSchema]:
    return await get_multiple_products(session, page_params, query_params=query_params)


async def update_single_product(
    session: AsyncSession, product_input: ProductUpdateSchema, product_id: str
) -> ProductOutputSchema:
    product_was_updated = 0

    if not (product_object := await if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)

    if product_object.legacy_product:
        raise ProductIsAlreadyLegacyException

    product_data = product_input.dict(exclude_none=True, exclude_unset=True)

    if product_data.get("name") and (product_object.name != product_input.name):
        product_name_check = await session.scalar(
            select(Product).filter(Product.name == product_input.name).limit(1)
        )
        if product_name_check:
            raise IsOccupied(Product.__name__, "name", product_input.name)

    if category_ids := product_data.get("category_ids"):
        incoming_categories = set(category_ids["id"])
        current_categories = set(category.id for category in product_object.categories)
        if to_delete := (current_categories - incoming_categories):
            await session.execute(
                delete(category_product_association_table).where(
                    Category.id.in_(to_delete)
                )
            )
            product_was_updated += 1

        if to_insert := incoming_categories:
            rows = [
                {"product_id": product_id, "category_id": category_id}
                for category_id in to_insert
            ]
            await session.execute(
                insert(category_product_association_table).values(rows)
            )
            product_was_updated += 1

        product_data.pop("category_ids")

    if product_data:
        statement = (
            update(Product).filter(Product.id == product_id).values(**product_data)
        )
        await session.execute(statement)
        product_was_updated += 1

    if product_was_updated:
        await session.commit()
        await session.refresh(product_object)

    return await get_single_product(session, product_id=product_id)


async def make_single_product_legacy(
    session: AsyncSession, product_id: str
) -> dict[str, str]:
    if not (product_object := await if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)

    if product_object.legacy_product:
        raise ProductIsAlreadyLegacyException

    product_object.legacy_product = True
    session.add(product_object)
    await session.commit()

    return {"message": "Product has been changed into a legacy product"}
