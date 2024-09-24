import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.services import create_issue
from src.apps.issues.schemas import StockIssueInputSchema
from src.apps.products.schemas.category_schemas import (
    CategoryIdListSchema,
    CategoryOutputSchema,
)
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.rack_level_slots.schemas import RackLevelSlotOutputSchema
from src.apps.rack_levels.schemas import RackLevelOutputSchema
from src.apps.racks.models import Rack
from src.apps.racks.schemas import RackOutputSchema
from src.apps.racks.services import get_all_racks
from src.apps.receptions.schemas import (
    ReceptionOutputSchema,
    ReceptionProductInputSchema,
)
from src.apps.receptions.services import create_reception, get_all_receptions
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.stocks.schemas.stock_schemas import (
    StockOutputSchema,
)
from src.apps.stocks.schemas.user_stock_schemas import UserStockOutputSchema
from src.apps.stocks.services.stock_services import get_every_stock
from src.apps.stocks.services.user_stock_services import get_all_user_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.models import WaitingRoom
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
from tests.test_rack_levels.conftest import db_rack_levels
from tests.test_racks.conftest import db_racks
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
    WaitingRoomInputSchemaFactory().generate() for _ in range(2)
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

    db_racks = await get_all_racks(
        async_session, PageParams(), output_schema=RackOutputSchema
    )
    for product, rack in zip(products, db_racks.results):
        rack = await if_exists(Rack, "id", rack.id, async_session)
        reception_input = ReceptionInputSchemaFactory().generate(
            products_data=[
                ReceptionProductInputSchemaFactory().generate(
                    product_id=product.id, rack_level_id=rack.rack_levels[0].id
                )
            ]
        )
        print(reception_input, "cd", db_racks.results)
        await create_reception(async_session, reception_input, db_staff_user.id)

    # one stock to the waiting room
    reception_input = ReceptionInputSchemaFactory().generate(
        products_data=[
            ReceptionProductInputSchemaFactory().generate(
                product_id=db_products.results[0].id,
                waiting_room_id=waiting_rooms[0].id,
            )
        ]
    )
    await create_reception(async_session, reception_input, db_staff_user.id)

    # one stock will be issued
    reception_input = ReceptionInputSchemaFactory().generate(
        products_data=[
            ReceptionProductInputSchemaFactory().generate(
                product_id=db_products.results[0].id,
                waiting_room_id=waiting_rooms[1].id,
            )
        ]
    )
    result = await create_reception(async_session, reception_input, db_staff_user.id)

    issue_input = IssueInputSchemaFactory().generate(
        stock_ids=[StockIssueInputSchema(id=result.stocks[0].id)]
    )
    await create_issue(async_session, issue_input, db_staff_user.id)
    await async_session.flush()

    waiting_room_with_no_stocks = await create_waiting_room(
        async_session, WaitingRoomInputSchemaFactory().generate(), testing=True
    )
    await async_session.refresh(waiting_room_with_no_stocks)
    await async_session.refresh(waiting_rooms[0])
    return await get_every_stock(async_session, PageParams())


@pytest_asyncio.fixture
async def db_user_stocks(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
) -> PagedResponseSchema[StockOutputSchema]:
    return await get_all_user_stocks(async_session, PageParams())
