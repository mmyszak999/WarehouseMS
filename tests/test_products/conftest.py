import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.category_schemas import (
    CategoryOutputSchema,
)
from src.apps.products.services.category_services import create_category, get_all_categories
from src.apps.products.services.product_services import create_product
from src.core.factory.category_factory import CategoryInputSchemaFactory

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

DB_CATEGORY_SCHEMAS = [CategoryInputSchemaFactory().generate() for _ in range(3)]


@pytest_asyncio.fixture
async def db_categories(async_session: AsyncSession) -> PagedResponseSchema[CategoryOutputSchema]:
    [await create_category(async_session, category) for category in DB_CATEGORY_SCHEMAS]
    return await get_all_categories(async_session, PageParams())