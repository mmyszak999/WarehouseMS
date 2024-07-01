import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sections.schemas import SectionOutputSchema
from src.apps.sections.services import create_section, get_all_sections
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.warehouse.schemas import WarehouseInputSchema, WarehouseOutputSchema
from src.core.factory.section_factory import SectionInputSchemaFactory
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
from tests.test_warehouse.conftest import db_warehouse


@pytest_asyncio.fixture
async def db_sections(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
) -> PagedResponseSchema[SectionOutputSchema]:
    section_inputs = [SectionInputSchemaFactory().generate()]
    [
        await create_section(async_session, section_input)
        for section_input in section_inputs
    ]
    return await get_all_sections(
        async_session, PageParams(), output_schema=SectionOutputSchema
    )
