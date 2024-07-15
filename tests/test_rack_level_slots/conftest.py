import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_level_slots.schemas import RackLevelSlotOutputSchema
from src.apps.rack_level_slots.services import get_all_rack_level_slots
from src.apps.rack_levels.schemas import RackLevelOutputSchema
from src.apps.racks.schemas import RackOutputSchema
from src.apps.racks.services import get_all_racks
from src.apps.sections.schemas import SectionOutputSchema
from src.core.factory.rack_level_slot_factory import RackLevelSlotInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
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


@pytest_asyncio.fixture
async def db_rack_level_slots(
    async_session: AsyncSession, db_sections: PagedResponseSchema[SectionOutputSchema]
) -> PagedResponseSchema[RackLevelSlotOutputSchema]:
    return await get_all_rack_level_slots(
        async_session, PageParams(), output_schema=RackLevelSlotOutputSchema
    )
