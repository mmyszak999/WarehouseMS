import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_levels.schemas import RackLevelOutputSchema
from src.apps.rack_levels.services import create_rack_level, get_all_rack_levels
from src.apps.racks.schemas import RackOutputSchema
from src.apps.racks.services import get_all_racks
from src.apps.racks.models import Rack
from src.core.factory.rack_level_factory import RackLevelInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.apps.sections.schemas import SectionOutputSchema
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
async def db_rack_levels(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema]
) -> PagedResponseSchema[RackLevelOutputSchema]:
    return await get_all_rack_levels(
        async_session, PageParams(), output_schema=RackLevelOutputSchema
    )
