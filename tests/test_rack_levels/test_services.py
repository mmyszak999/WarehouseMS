import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.racks.models import Rack
from src.apps.racks.schemas import RackInputSchema, RackOutputSchema, RackUpdateSchema
from src.apps.racks.services import (
    create_rack,
    get_all_racks,
    get_single_rack,
)
from src.apps.rack_levels.services import (
    create_rack_level,
    get_all_rack_levels,
    get_single_rack_level,
    manage_rack_level_state,
    update_single_rack_level,
    delete_single_rack_level
)
from src.apps.rack_levels.models import RackLevel
from src.apps.rack_levels.schemas import (
    RackLevelInputSchema, RackLevelOutputSchema, RackLevelUpdateSchema
)
from src.apps.sections.models import Section
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.sections.services import create_section, get_single_section
from src.core.exceptions import (
    DoesNotExist,
    ServiceException,
)
from src.core.factory.rack_factory import (
    RackInputSchemaFactory,
    RackUpdateSchemaFactory,
)
from src.core.factory.rack_level_factory import (
    RackLevelInputSchemaFactory,
    RackLevelUpdateSchemaFactory,
)
from src.core.factory.section_factory import SectionInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import db_categories, db_products
from tests.test_racks.conftest import db_racks
from tests.test_sections.conftest import db_sections
from tests.test_stocks.conftest import db_stocks
from tests.test_rack_levels.conftest import db_rack_levels
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_warehouse.conftest import db_warehouse


@pytest.mark.asyncio
async def test_raise_exception_when_rack_level_created_with_nonexistent_level(
    async_session: AsyncSession
):
    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=generate_uuid(),
        rack_level_number=5
    )

    with pytest.raises(DoesNotExist):
        await create_rack_level(async_session, rack_level_input)