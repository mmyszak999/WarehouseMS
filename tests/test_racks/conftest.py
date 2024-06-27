import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sections.schemas import SectionOutputSchema
from src.apps.racks.services import create_rack, get_all_racks
from src.apps.racks.schemas import RackOutputSchema
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.warehouse.schemas import WarehouseInputSchema, WarehouseOutputSchema
from src.core.factory.rack_factory import RackInputSchemaFactory
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
async def db_racks(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
) -> PagedResponseSchema[RackOutputSchema]:
    for section in db_sections.results:
        for _ in range(section.max_racks - 2):
            await create_rack(
                async_session, RackInputSchemaFactory().generate(section_id=section.id)
            )
            
    return await get_all_racks(async_session, PageParams(), output_schema=RackOutputSchema)
