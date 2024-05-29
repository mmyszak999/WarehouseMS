from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.models import Product
from src.apps.receptions.models import Reception
from src.apps.receptions.schemas import (
    ReceptionBasicOutputSchema,
    ReceptionInputSchema,
    ReceptionOutputSchema,
    ReceptionUpdateSchema,
)
from src.apps.stocks.models import Stock
from src.apps.stocks.services import create_stocks
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists



async def base_create_reception(
    session: AsyncSession, reception_input: ReceptionInputSchema, user_id: str,
    testing: bool = False
):
    reception_input = reception_input.dict(exclude_none=True, exclude_unset=True)
    products_data = reception_input["products_data"]
    if testing:
        new_reception = Reception(
        user_id=user_id, description=reception_input.get("description")
        )
        session.add(new_reception)
        await session.commit()
        return new_reception

    if product_ids := [product.pop("product_id") for product in products_data]:
        products = await session.scalars(
            select(Product).where(Product.id.in_(product_ids))
        )
        products = products.unique().all()
        if not len(set(product_ids)) == len(products):
            raise ServiceException("Wrong products!")

    product_counts = [product.pop("product_count") for product in products_data]
    new_reception = Reception(
        user_id=user_id, description=reception_input.get("description")
    )
    session.add(new_reception)
    await session.flush()
    return products, product_counts, new_reception


async def create_reception(
    session: AsyncSession, reception_input: ReceptionInputSchema, user_id: str
) -> ReceptionOutputSchema:
    
    products, product_counts, new_reception = await base_create_reception(
        session, reception_input, user_id
    )
    await create_stocks(session, products, product_counts, new_reception.id)

    await session.commit()
    await session.refresh(new_reception)

    return ReceptionOutputSchema.from_orm(new_reception)


async def get_single_reception(
    session: AsyncSession, reception_id: int
) -> ReceptionOutputSchema:
    if not (
        reception_object := await if_exists(Reception, "id", reception_id, session)
    ):
        raise DoesNotExist(Reception.__name__, "id", reception_id)

    return ReceptionOutputSchema.from_orm(reception_object)


async def get_all_receptions(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[ReceptionBasicOutputSchema]:
    query = select(Reception)

    return await paginate(
        query=query,
        response_schema=ReceptionBasicOutputSchema,
        table=Reception,
        page_params=page_params,
        session=session,
    )


async def update_single_reception(
    session: AsyncSession, reception_input: ReceptionUpdateSchema, reception_id: int
) -> ReceptionOutputSchema:
    if not (
        reception_object := await if_exists(Reception, "id", reception_id, session)
    ):
        raise DoesNotExist(Reception.__name__, "id", reception_id)

    reception_data = reception_input.dict(exclude_unset=True)

    if reception_data:
        statement = (
            update(Reception)
            .filter(Reception.id == reception_id)
            .values(**reception_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(reception_object)

    return await get_single_reception(session, reception_id=reception_id)
