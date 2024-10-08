import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.schemas import IssueOutputSchema
from src.apps.issues.services import create_issue, get_all_issues
from src.apps.products.schemas.category_schemas import (
    CategoryIdListSchema,
    CategoryOutputSchema,
)
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.factory.issue_factory import IssueInputSchemaFactory
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_products.conftest import db_categories, db_products
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)
from tests.test_waiting_rooms.conftest import db_waiting_rooms


@pytest_asyncio.fixture
async def db_issues(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
) -> PagedResponseSchema[IssueOutputSchema]:
    return await get_all_issues(async_session, PageParams())
