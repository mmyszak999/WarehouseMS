import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.services import create_issue
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
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.stocks.schemas.stock_schemas import (
    StockIssueInputSchema,
    StockOutputSchema,
)
from src.apps.stocks.schemas.user_stock_schemas import UserStockOutputSchema
from src.apps.stocks.services.stock_services import get_all_stocks
from src.apps.stocks.services.user_stock_services import get_all_user_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.schemas import WaitingRoomOutputSchema
from src.apps.waiting_rooms.services import create_waiting_room, get_all_waiting_rooms
from src.core.factory.issue_factory import IssueInputSchemaFactory
from src.core.factory.reception_factory import (
    ReceptionInputSchemaFactory,
    ReceptionProductInputSchemaFactory,
)
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.factory.waiting_room_factory import WaitingRoomInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_products.conftest import db_categories, db_products
from tests.test_sections.conftest import db_sections
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)

DB_WAITING_ROOMS_SCHEMAS = [
    WaitingRoomInputSchemaFactory().generate() for _ in range(3)
]


@pytest_asyncio.fixture
async def db_stocks(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
) -> PagedResponseSchema[StockOutputSchema]:
    waiting_rooms = [
        await create_waiting_room(async_session, waiting_room, testing=True)
        for waiting_room in DB_WAITING_ROOMS_SCHEMAS
    ]
    products = db_products.results + db_products.results
    for product in products:
        reception_input = ReceptionInputSchemaFactory().generate(
            products_data=[
                ReceptionProductInputSchemaFactory().generate(product_id=product.id)
            ]
        )
        await create_reception(async_session, reception_input, db_staff_user.id)

    stocks = await get_all_stocks(async_session, PageParams())
    issue_input = IssueInputSchemaFactory().generate(
        stock_ids=[StockIssueInputSchema(id=stocks.results[-1].id)]
    )
    await create_issue(async_session, issue_input, db_staff_user.id)
    await async_session.flush()
    [await async_session.refresh(waiting_room) for waiting_room in waiting_rooms]

    return await get_all_stocks(async_session, PageParams())


@pytest_asyncio.fixture
async def db_user_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
) -> PagedResponseSchema[StockOutputSchema]:
    return await get_all_user_stocks(async_session, PageParams())
