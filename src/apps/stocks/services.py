from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.receptions.models import Reception
from src.apps.receptions.schemas import (
    ReceptionInputSchema,
    ReceptionOutputSchema
)
from src.apps.products.models import Product
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas import StockInputSchema
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_stocks(
    session: AsyncSession, products: list[Product],
    product_counts: dict[str, int], reception_id: str
) -> None:
    for product, product_count, in zip(products, product_counts):
        weight = product_count * product.weight
        stock_input = StockInputSchema(
            weight=weight,
            product_count=product_count,
            product_id=product.id,
            reception_id=reception_id
        )
        new_stock = Stock(
            **stock_input.dict()
        )
        session.add(new_stock)
    await session.flush()
        