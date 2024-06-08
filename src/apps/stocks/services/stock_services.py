from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.models import Product
from src.apps.stocks.models import Stock, UserStock
from src.apps.stocks.schemas.stock_schemas import (
    StockBasicOutputSchema,
    StockInputSchema,
    StockOutputSchema,
)
from src.apps.stocks.services.user_stock_services import create_user_stock_object
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.services import manage_waiting_room_state
from src.core.exceptions import (
    AlreadyExists,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    MissingProductDataException,
    NoAvailableWaitingRoomsException,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists
from src.core.utils.time import get_current_time


async def create_stocks(
    session: AsyncSession,
    user_id: str,
    products: list[Product] = [],
    product_counts: list[int] = [],
    reception_id: str = None,
    testing: bool = False,
    input_schemas: list[StockInputSchema] = None,
) -> list[Stock]:
    stock_list = []
    if testing and input_schemas:
        for schema in input_schemas:
            new_stock = Stock(**schema.dict())
            session.add(new_stock)
            stock_list.append(new_stock)
        await session.commit()
        return stock_list

    if not (products or product_counts):
        raise MissingProductDataException

    for (
        product,
        product_count,
    ) in zip(products, product_counts):
        stock_weight = product_count * product.weight
        available_waiting_room = await session.execute(
            select(WaitingRoom)
            .filter(
                WaitingRoom.available_slots >= 1,
                WaitingRoom.available_stock_weight >= stock_weight,
            )
            .limit(1)
        )
        available_waiting_room = available_waiting_room.scalar()
        if not available_waiting_room:
            raise NoAvailableWaitingRoomsException(
                product.name, product_count, stock_weight
            )

        stock_input = StockInputSchema(
            weight=stock_weight,
            product_count=product_count,
            product_id=product.id,
            reception_id=reception_id,
            waiting_room_id=available_waiting_room.id,
        )
        new_stock = Stock(**stock_input.dict())
        session.add(new_stock)
        stock_list.append(new_stock)
        available_waiting_room = await manage_waiting_room_state(
            available_waiting_room, stocks_involved=True, stock_object=new_stock
        )
        session.add(available_waiting_room)
        await session.flush()
        user_stock_object = await create_user_stock_object(
            session, new_stock.id, user_id, available_waiting_room.id
        )
        print(user_stock_object)
        raise Exception
    return stock_list


async def get_single_stock(
    session: AsyncSession, stock_id: int, can_get_issued: bool = False
) -> StockOutputSchema:
    if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
        raise DoesNotExist(Stock.__name__, "id", stock_id)

    if (not can_get_issued) and stock_object.is_issued:
        raise CannotRetrieveIssuedStockException
    return StockOutputSchema.from_orm(stock_object)


async def get_multiple_stocks(
    session: AsyncSession,
    page_params: PageParams,
    schema: BaseModel = StockBasicOutputSchema,
    get_issued: bool = False,
) -> Union[
    PagedResponseSchema[StockBasicOutputSchema],
    PagedResponseSchema[StockOutputSchema],
]:
    query = select(Stock)
    if not get_issued:
        query = query.filter(Stock.is_issued == False)

    return await paginate(
        query=query,
        response_schema=schema,
        table=Stock,
        page_params=page_params,
        session=session,
    )


async def get_all_stocks(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[StockOutputSchema]:
    return await get_multiple_stocks(
        session, page_params, schema=StockOutputSchema, get_issued=True
    )


async def get_all_available_stocks(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[StockBasicOutputSchema]:
    return await get_multiple_stocks(session, page_params)


async def issue_stocks(
    session: AsyncSession, stocks: list[Stock], issue_id: str
) -> list[Stock]:
    for stock in stocks:
        if stock.waiting_room:
            stock_waiting_room = await if_exists(
                WaitingRoom, "id", stock.waiting_room_id, session
            )
            stock_waiting_room = await manage_waiting_room_state(
                waiting_room_object=stock_waiting_room,
                stocks_involved=True,
                adding_stock_to_waiting_room=False,
                stock_object=stock,
            )
            session.add(stock_waiting_room)
            stock.issue_id = issue_id
            stock.is_issued = True
            stock.updated_at = get_current_time()
            stock.waiting_room_id = None
            stock.waiting_room = None
            session.add(stock)
    return stocks
