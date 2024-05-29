import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.category_schemas import (
    CategoryIdListSchema,
    CategoryOutputSchema,
)
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.issues.schemas import IssueOutputSchema
from src.apps.stocks.services import (
    get_all_stocks
)
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.apps.issues.services import get_all_issues, create_issue
from src.apps.stocks.schemas import StockIssueInputSchema
from src.core.factory.issue_factory import IssueInputSchemaFactory
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)
from tests.test_products.conftest import (
    db_categories,
    db_products
)
from tests.test_stocks.conftest import db_stocks


@pytest_asyncio.fixture
async def db_issues(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema
) -> PagedResponseSchema[IssueOutputSchema]:
    issue_input = IssueInputSchemaFactory().generate(
        stock_ids=[StockIssueInputSchema(id=db_stocks.results[2].id)]
    )
    await create_issue(async_session, issue_input, db_staff_user.id)
    return await get_all_issues(async_session, PageParams())
