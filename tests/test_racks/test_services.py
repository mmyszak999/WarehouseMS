import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.racks.models import Rack
from src.apps.racks.schemas import (
    RackInputSchema,
    RackOutputSchema,
    RackUpdateSchema,
)
from src.apps.racks.services import (
    create_rack,
    delete_single_rack,
    get_all_racks,
    get_single_rack,
    manage_rack_state,
    update_single_rack,
)
from src.apps.sections.services import (
    create_section
)
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.stocks.services.stock_services import create_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.services import create_waiting_room
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.apps.warehouse.services import create_warehouse
from src.apps.sections.schemas import (
    SectionOutputSchema
)
from src.core.exceptions import (
    DoesNotExist,
    NotEnoughWarehouseResourcesException,
    ServiceException,
    TooLittleRacksAmountException,
    TooLittleWeightAmountException,
    WarehouseDoesNotExistException,
    RackIsNotEmptyException,
    NotEnoughSectionResourcesException
)
from src.core.factory.rack_factory import (
    RackInputSchemaFactory,
    RackUpdateSchemaFactory,
)
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.factory.waiting_room_factory import WaitingRoomInputSchemaFactory
from src.core.factory.warehouse_factory import (
    WarehouseInputSchemaFactory,
    WarehouseUpdateSchemaFactory,
)
from src.core.factory.section_factory import (
    SectionInputSchemaFactory
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import db_categories, db_products
from tests.test_racks.conftest import db_racks
from tests.test_stocks.conftest import db_stocks
from tests.test_sections.conftest import db_sections
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_warehouse.conftest import db_warehouse
from tests.test_racks.conftest import db_racks


@pytest.mark.asyncio
async def test_raise_exception_when_rack_created_with_nonexistent_section(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema]
):
    rack_input = RackInputSchemaFactory().generate(section_id=generate_uuid())

    with pytest.raises(DoesNotExist):
        await create_rack(async_session, rack_input)


@pytest.mark.asyncio
async def test_raise_exception_when_section_does_not_have_slots_for_another_rack(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema]
):
    section_input = SectionInputSchemaFactory().generate(max_racks=1)
    section = await create_section(async_session, section_input)

    rack_input_1 = RackInputSchemaFactory().generate(section_id=section.id)
    await create_rack(async_session, rack_input_1)
    
    rack_input_2 = RackInputSchemaFactory().generate(section_id=section.id)

    with pytest.raises(NotEnoughSectionResourcesException):
        await create_rack(async_session, rack_input_2)


@pytest.mark.asyncio
async def test_raise_exception_when_there_is_no_available_weight_to_reserve_for_another_rack(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema]
):
    section_input = SectionInputSchemaFactory().generate(max_weight=300)
    section = await create_section(async_session, section_input)

    rack_input = RackInputSchemaFactory().generate(section_id=section.id, max_weight=3001)
    
    with pytest.raises(NotEnoughSectionResourcesException):
        await create_rack(async_session, rack_input)


@pytest.mark.asyncio
async def test_if_single_rack_is_returned(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack = await get_single_rack(async_session, db_racks.results[0].id)

    assert rack.id == db_racks.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_when_getting_nonexistent_rack(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_rack(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_racks_are_returned(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    racks = await get_all_racks(async_session, PageParams())

    assert racks.total == db_racks.total