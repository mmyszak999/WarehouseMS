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
from src.apps.stocks.services.stock_services import create_stocks
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    MissingReceptionDataException,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def base_create_reception(
    session: AsyncSession,
    user_id: str,
    reception_input: ReceptionInputSchema = None,
    testing: bool = False,
):
    if testing:
        new_reception = Reception(user_id=user_id)
        session.add(new_reception)
        await session.commit()
        return new_reception

    if (reception_input is None) or not (
        reception_input := reception_input.dict(exclude_unset=True)
    ):
        raise MissingReceptionDataException

    products_data = reception_input["products_data"]
    if product_ids := [product.pop("product_id") for product in products_data]:
        products = await session.scalars(
            select(Product).where(Product.id.in_(product_ids))
        )
        products = products.unique().all()
        if not len(set(product_ids)) == len(products):
            raise ServiceException("Wrong products!")

    product_counts = [product.pop("product_count") for product in products_data]
    if not len(products) == len(product_counts):
        raise ServiceException("Products does not match the product count data")

    waiting_rooms_ids = [
        product.get("waiting_room_id", None) for product in products_data
    ]

    rack_level_slots_ids = [
        product.get("rack_level_slot_id", None) for product in products_data
    ]

    rack_level_ids = [product.get("rack_level_id", None) for product in products_data]

    new_reception = Reception(
        user_id=user_id, description=reception_input.get("description")
    )
    session.add(new_reception)
    await session.flush()
    return (
        products,
        product_counts,
        new_reception,
        waiting_rooms_ids,
        rack_level_slots_ids,
        rack_level_ids,
    )


async def create_reception(
    session: AsyncSession, reception_input: ReceptionInputSchema, user_id: str
) -> ReceptionOutputSchema:
    (
        products,
        product_counts,
        new_reception,
        waiting_room_ids,
        rack_level_slots_ids,
        rack_level_ids,
    ) = await base_create_reception(session, user_id, reception_input)
    stocks = await create_stocks(
        session,
        user_id,
        waiting_room_ids,
        rack_level_slots_ids,
        rack_level_ids,
        products,
        product_counts,
        reception_id=new_reception.id
    )

    await session.commit()
    [await session.refresh(stock) for stock in stocks]
    await session.refresh(new_reception)

    return ReceptionOutputSchema.from_orm(new_reception)


async def get_single_reception(
    session: AsyncSession, reception_id: str
) -> ReceptionOutputSchema:
    if not (
        reception_object := await if_exists(Reception, "id", reception_id, session)
    ):
        raise DoesNotExist(Reception.__name__, "id", reception_id)

    return ReceptionOutputSchema.from_orm(reception_object)


async def get_all_receptions(
    session: AsyncSession, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[ReceptionBasicOutputSchema]:
    query = select(Reception)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Reception)

    return await paginate(
        query=query,
        response_schema=ReceptionBasicOutputSchema,
        table=Reception,
        page_params=page_params,
        session=session,
    )


async def update_single_reception(
    session: AsyncSession, reception_input: ReceptionUpdateSchema, reception_id: str
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
