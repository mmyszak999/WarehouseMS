from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.models import Product
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas import (
    StockBasicOutputSchema,
    StockInputSchema,
    StockOutputSchema,
)
from src.core.exceptions import (
    AlreadyExists,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    MissingProductDataException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists
from src.core.utils.time import get_current_time


async def create_stocks(
    session: AsyncSession,
    products: list[Product] = [],
    product_counts: list[int] = [],
    reception_id: str = None,
    testing: bool = False,
    input_schemas: list[StockInputSchema] = None
) -> list[Stock]:
    stock_list = []
    if testing and input_schemas:
        for schema in input_schemas:
            new_stock = Stock(**schema.dict())
            session.add(new_stock)
            stock_list.append(new_stock)
        await session.flush()
        return stock_list
    
    if not (products or product_counts):
        raise MissingProductDataException
            
    for (
        product,
        product_count,
    ) in zip(products, product_counts):
        weight = product_count * product.weight
        stock_input = StockInputSchema(
            weight=weight,
            product_count=product_count,
            product_id=product.id,
            reception_id=reception_id,
        )
        new_stock = Stock(**stock_input.dict())
        session.add(new_stock)
        stock_list.append(new_stock)
    await session.flush()
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

    """query = query.join(
        category_product_association_table,
        Product.id == category_product_association_table.c.product_id,
        isouter=True,
    ).join(
        Category,
        category_product_association_table.c.category_id == Category.id,
        isouter=True,
    )"""

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
        stock.issue_id = issue_id
        stock.is_issued = True
        stock.updated_at = get_current_time()
        session.add(stock)
    await session.flush()
    return stocks
