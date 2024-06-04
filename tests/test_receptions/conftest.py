import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.receptions.schemas import (
    ReceptionOutputSchema,
    ReceptionProductInputSchema,
)
from src.apps.receptions.services import get_all_receptions
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_products.conftest import db_categories, db_products
from tests.test_stocks.conftest import db_stocks
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
async def db_receptions(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema]
) -> PagedResponseSchema[ReceptionOutputSchema]:
    return await get_all_receptions(async_session, PageParams())
