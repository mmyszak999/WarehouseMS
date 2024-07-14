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
from src.core.factory.rack_factory import RackInputSchemaFactory
from src.apps.racks.schemas import RackOutputSchema
from src.apps.racks.services import create_rack, get_all_racks
from src.core.factory.rack_level_factory import RackLevelInputSchemaFactory
from src.apps.rack_levels.schemas import RackLevelOutputSchema
from src.apps.rack_levels.services import create_rack_level, get_all_rack_levels


@pytest_asyncio.fixture
async def db_sections(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
) -> PagedResponseSchema[SectionOutputSchema]:
    section_inputs = [SectionInputSchemaFactory().generate()]
    sections = [
        await create_section(async_session, section_input)
        for section_input in section_inputs
    ]
    
    racks = []
    for section in sections:
        for _ in range(section.max_racks - 2):
            racks.append(await create_rack(
                async_session, RackInputSchemaFactory().generate(section_id=section.id)
            ))
    
    for rack in racks:
        for level_number in range(1, rack.max_levels-2):
            await create_rack_level(
                async_session,
                RackLevelInputSchemaFactory().generate(
                    rack_id=rack.id, rack_level_number=level_number
                ),
            )
    
    return await get_all_sections(
        async_session, PageParams(), output_schema=SectionOutputSchema
    )
