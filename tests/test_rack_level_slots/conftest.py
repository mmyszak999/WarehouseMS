import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_levels.schemas import RackLevelOutputSchema
from src.apps.rack_levels.services import create_rack_level, get_all_rack_levels
from src.apps.racks.schemas import RackOutputSchema
from src.apps.racks.services import get_all_racks
from src.core.factory.rack_level_factory import RackLevelInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_racks.conftest import db_racks
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)


@pytest_asyncio.fixture
async def db_rack_levels(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
) -> PagedResponseSchema[RackLevelOutputSchema]:
    for rack in db_racks.results:
        for level_number in range(1, rack.max_levels - 1):
            await create_rack_level(
                async_session,
                RackLevelInputSchemaFactory().generate(
                    rack_id=rack.id, rack_level_number=level_number
                ),
            )

    return await get_all_rack_levels(
        async_session, PageParams(), output_schema=RackLevelOutputSchema
    )
