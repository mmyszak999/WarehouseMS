from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.receptions.models import Reception
from src.apps.receptions.schemas import (
    ReceptionInputSchema,
    ReceptionOutputSchema
)
from src.apps.products.models import Product
from src.apps.stocks.models import Stock
from src.apps.stocks.services import create_stocks
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_reception(
    session: AsyncSession, reception_input: ReceptionInputSchema,
    user_id: str
) -> ReceptionOutputSchema:
    products_data = reception_input.dict()["products_data"]
    if product_ids := [product.pop("product_id") for product in products_data]:
        products = await session.scalars(
            select(Product).where(Product.id.in_(product_ids))
        )
        products = products.unique().all()
        if not len(set(product_ids)) == len(products):
            raise ServiceException("Wrong products!")
    
    product_counts = [product.pop("product_count") for product in products_data]
    new_reception = Reception(user_id=user_id)
    session.add(new_reception)
    await session.flush()
    await create_stocks(session, products, product_counts, new_reception.id)
    
    await session.commit()
    await session.refresh(new_reception)
    print([s.__dict__ for s in new_reception.stocks])
    
    return ReceptionOutputSchema.from_orm(new_reception)


"""async def get_single_category(
    session: AsyncSession, category_id: int
) -> CategoryOutputSchema:
    if not (category_object := await if_exists(Category, "id", category_id, session)):
        raise DoesNotExist(Category.__name__, "id", category_id)

    return CategoryOutputSchema.from_orm(category_object)


async def get_all_categories(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[CategoryOutputSchema]:
    query = select(Category)

    return await paginate(
        query=query,
        response_schema=CategoryOutputSchema,
        table=Category,
        page_params=page_params,
        session=session,
    )


async def update_single_category(
    session: AsyncSession, category_input: CategoryUpdateSchema, category_id: int
) -> CategoryOutputSchema:
    if not (category_object := await if_exists(Category, "id", category_id, session)):
        raise DoesNotExist(Category.__name__, "id", category_id)

    category_data = category_input.dict(exclude_unset=True)

    if category_data:
        category_name_check = await session.scalar(
            select(Category).filter(Category.name == category_input.name).limit(1)
        )
        if category_name_check:
            raise IsOccupied(Category.__name__, "name", category_input.name)

        statement = (
            update(Category).filter(Category.id == category_id).values(**category_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(category_object)

    return await get_single_category(session, category_id=category_id)


async def delete_single_category(session: AsyncSession, category_id: str):
    if not (await if_exists(Category, "id", category_id, session)):
        raise DoesNotExist(Category.__name__, "id", category_id)

    statement = delete(Category).filter(Category.id == category_id)
    result = await session.execute(statement)
    await session.commit()

    return result
"""