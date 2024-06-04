import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.category_schemas import (
    CategoryIdListSchema,
    CategoryOutputSchema,
)
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.receptions.schemas import (
    ReceptionOutputSchema,
    ReceptionProductInputSchema,
)
from src.apps.receptions.services import create_reception, get_all_receptions
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.stocks.services import get_all_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.schemas import WaitingRoomOutputSchema
from src.core.factory.reception_factory import (
    ReceptionInputSchemaFactory,
    ReceptionProductInputSchemaFactory,
)
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_products.conftest import db_categories, db_products
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)


@pytest_asyncio.fixture
async def db_stocks(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
) -> PagedResponseSchema[StockOutputSchema]:
    for product in db_products.results:
        reception_input = ReceptionInputSchemaFactory().generate(
            products_data=[
                ReceptionProductInputSchemaFactory().generate(product_id=product.id)
            ]
        )
        await create_reception(async_session, reception_input, db_staff_user.id)

    return await get_all_stocks(async_session, PageParams())
