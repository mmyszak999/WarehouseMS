import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.racks.models import Rack
from src.apps.racks.schemas import RackInputSchema, RackOutputSchema, RackUpdateSchema
from src.apps.racks.services import (
    create_rack,
    delete_single_rack,
    get_all_racks,
    get_single_rack,
    manage_rack_state,
    update_single_rack,
)
from src.apps.sections.models import Section
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.sections.services import create_section, get_single_section
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.stocks.services.stock_services import create_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.services import create_waiting_room
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.apps.warehouse.services import create_warehouse
from src.core.exceptions import (
    DoesNotExist,
    NotEnoughSectionResourcesException,
    NotEnoughWarehouseResourcesException,
    RackIsNotEmptyException,
    ServiceException,
    TooLittleRackLevelsAmountException,
    TooLittleRacksAmountException,
    TooLittleWeightAmountException,
    WarehouseDoesNotExistException,
    WeightLimitExceededException,
)
from src.core.factory.rack_factory import (
    RackInputSchemaFactory,
    RackUpdateSchemaFactory,
)
from src.core.factory.section_factory import SectionInputSchemaFactory
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.factory.waiting_room_factory import WaitingRoomInputSchemaFactory
from src.core.factory.warehouse_factory import (
    WarehouseInputSchemaFactory,
    WarehouseUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import db_categories, db_products
from tests.test_racks.conftest import db_racks
from tests.test_sections.conftest import db_sections
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_warehouse.conftest import db_warehouse


@pytest.mark.asyncio
async def test_raise_exception_when_rack_created_with_nonexistent_section(
    async_session: AsyncSession, db_sections: PagedResponseSchema[SectionOutputSchema]
):
    rack_input = RackInputSchemaFactory().generate(section_id=generate_uuid())

    with pytest.raises(DoesNotExist):
        await create_rack(async_session, rack_input)


@pytest.mark.asyncio
async def test_raise_exception_when_section_does_not_have_slots_for_another_rack(
    async_session: AsyncSession, db_sections: PagedResponseSchema[SectionOutputSchema]
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
    async_session: AsyncSession, db_sections: PagedResponseSchema[SectionOutputSchema]
):
    section_input = SectionInputSchemaFactory().generate(max_weight=300)
    section = await create_section(async_session, section_input)

    rack_input = RackInputSchemaFactory().generate(
        section_id=section.id, max_weight=3001
    )

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


@pytest.mark.asyncio
async def test_raise_exception_when_rack_not_provided_when_managing_state(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    with pytest.raises(ServiceException):
        await manage_rack_state()


@pytest.mark.asyncio
async def test_if_rack_max_levels_are_correctly_managed(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack = await if_exists(Rack, "id", db_racks.results[0].id, async_session)
    # decrement max_levels by 1
    rack = await manage_rack_state(rack, levels_involved=True)

    assert rack.available_levels == db_racks.results[0].available_levels + 1


@pytest.mark.asyncio
async def test_if_rack_weight_limits_are_correctly_managed(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack = await if_exists(Rack, "id", db_racks.results[0].id, async_session)
    # decrement max_weight by some weight
    weight = 100
    rack = await manage_rack_state(rack, weight_involved=True, stock_weight=weight)

    assert rack.available_weight == db_racks.results[0].available_weight + weight


@pytest.mark.asyncio
async def test_raise_exception_when_weight_is_not_provided_while_managiing_weight_values(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack = await if_exists(Rack, "id", db_racks.results[0].id, async_session)
    with pytest.raises(ServiceException):
        await manage_rack_state(rack, weight_involved=True)


@pytest.mark.asyncio
async def test_if_rack_limits_are_correctly_managed_when_changing_max_weight_and_levels(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate()
    section_output = await create_section(async_session, section_input)

    rack_input = RackInputSchemaFactory().generate(section_id=section_output.id)
    rack_output = await create_rack(async_session, rack_input)

    rack = await if_exists(Rack, "id", rack_output.id, async_session)
    new_max_weight = 548
    new_max_levels = 10

    updated_rack = await manage_rack_state(
        rack, max_weight=new_max_weight, max_levels=new_max_levels
    )

    assert updated_rack.available_levels == rack_output.available_levels + (
        new_max_levels - rack_output.max_levels
    )

    assert updated_rack.available_weight == rack_output.available_weight + (
        new_max_weight - rack_output.max_weight
    )

    # come here when rackLevel created with the updated logic for Rack
    # assert updated_rack.weight_to_reserve == rack.weight_to_reserve


"""
come here when rackLevel created with the updated logic for Rack
@pytest.mark.asyncio
async def test_if_section_reserved_weight_limits_are_correctly_managed(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate()
    section_output = await create_section(async_session, section_input)

    section = await if_exists(Section, "id", section_output.id, async_session)
    weight_difference = -10
    updated_section = await manage_section_state(
        section, reserved_weight_involved=True, stock_weight=weight_difference
    )


    assert (
        updated_section.reserved_weight
        == section_output.reserved_weight - weight_difference
    )
    assert (
        updated_section.weight_to_reserve
        == section_output.weight_to_reserve + weight_difference
    )


@pytest.mark.asyncio
async def test_if_section_reserved_weight_limits_are_correctly_managed_when_updating_max_rack_weight(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate()
    section_output = await create_section(async_session, section_input)

    section = await if_exists(Section, "id", section_output.id, async_session)
    rack_weight_difference = 50
    updated_section = await manage_section_state(
        section, max_weight=section.max_weight, stock_weight=rack_weight_difference
    )

    assert updated_section.available_weight == section.available_weight
    assert (
        updated_section.weight_to_reserve
        == section_output.weight_to_reserve - rack_weight_difference
    )
    assert (
        updated_section.reserved_weight
        == section_output.reserved_weight + rack_weight_difference
    )"""


@pytest.mark.asyncio
async def test_raise_exception_when_updating_nonexistent_rack(
    async_session: AsyncSession,
):
    rack_input = RackUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_rack(async_session, rack_input, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_new_max_weight_smaller_than_occupied_weight_amount_when_updating_rack(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate()
    section = await create_section(async_session, section_input)

    rack_input = RackInputSchemaFactory().generate(section_id=section.id)
    rack_output = await create_rack(async_session, rack_input)
    rack_object = await if_exists(Rack, "id", rack_output.id, async_session)

    rack_object.occupied_weight = 3
    async_session.add(rack_object)
    await async_session.commit()

    rack_input = RackUpdateSchemaFactory().generate(max_weight=2)

    with pytest.raises(TooLittleWeightAmountException):
        await update_single_rack(async_session, rack_input, rack_object.id)


"""
come here when rackLevel created with the updated logic for Rack
@pytest.mark.asyncio
async def test_raise_exception_when_new_max_weight_smaller_than_reserved_weight_amount(
    async_session: AsyncSession,
):
    warehouse_input = WarehouseInputSchemaFactory().generate(max_sections=1)
    warehouse = await create_warehouse(async_session, warehouse_input)

    section_input = SectionInputSchemaFactory().generate()
    section = await create_section(async_session, section_input)

    section = await if_exists(Section, "id", section.id, async_session)
    section.reserved_weight = 3
    async_session.add(section)
    await async_session.commit()

    section_input = SectionUpdateSchemaFactory().generate(max_weight=2)

    with pytest.raises(TooLittleWeightAmountException):
        await update_single_section(async_session, section_input, section.id)"""


@pytest.mark.asyncio
async def test_raise_exception_while_updating_when_new_max_weight_bigger_than_max_weight_and_section_weight_to_reserve_combined(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate(max_weight=1000)
    section_output = await create_section(async_session, section_input)
    section_object = await if_exists(Section, "id", section_output.id, async_session)

    rack_input = RackInputSchemaFactory().generate(
        section_id=section_object.id, max_weight=500
    )
    rack_output = await create_rack(async_session, rack_input)
    rack_object = await if_exists(Rack, "id", rack_output.id, async_session)

    rack_input = RackUpdateSchemaFactory().generate(max_weight=1100)

    with pytest.raises(WeightLimitExceededException):
        await update_single_rack(async_session, rack_input, rack_object.id)


@pytest.mark.asyncio
async def test_check_if_section_state_managed_correctly_when_rack_max_weight_updated(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate(max_weight=1000)
    section_output = await create_section(async_session, section_input)

    rack_input_1 = RackInputSchemaFactory().generate(
        section_id=section_output.id, max_weight=500
    )
    rack_output = await create_rack(async_session, rack_input_1)
    rack_object = await if_exists(Rack, "id", rack_output.id, async_session)
    section_before = await get_single_section(async_session, section_output.id)

    rack_input_2 = RackUpdateSchemaFactory().generate(max_weight=400)
    rack_output = await update_single_rack(async_session, rack_input_2, rack_object.id)
    section_after = await get_single_section(async_session, section_output.id)

    assert section_before.reserved_weight == section_after.reserved_weight + (
        rack_input_1.max_weight - rack_input_2.max_weight
    )

    assert section_before.weight_to_reserve == section_after.weight_to_reserve - (
        rack_input_1.max_weight - rack_input_2.max_weight
    )


@pytest.mark.asyncio
async def test_raise_exception_when_new_max_levels_lower_than_occupied_levels(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    rack_input_1 = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=5
    )
    rack_output = await create_rack(async_session, rack_input_1)
    rack_object = await if_exists(Rack, "id", rack_output.id, async_session)

    rack_object.occupied_levels = 2
    async_session.add(rack_object)
    await async_session.commit()

    rack_input_2 = RackUpdateSchemaFactory().generate(max_levels=1)
    with pytest.raises(TooLittleRackLevelsAmountException):
        await update_single_rack(async_session, rack_input_2, rack_object.id)


@pytest.mark.asyncio
async def test_raise_exception_when_deleting_nonexistent_rack(
    async_session: AsyncSession, db_racks: PagedResponseSchema[RackOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await delete_single_rack(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_deleting_rack_with_occupied_weight(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)
    rack_object = await if_exists(Rack, "id", rack_output.id, async_session)

    rack_object.occupied_weight = 5
    async_session.add(rack_object)
    await async_session.commit()

    with pytest.raises(RackIsNotEmptyException):
        await delete_single_rack(async_session, rack_object.id)


@pytest.mark.asyncio
async def test_check_if_section_state_managed_correctly_when_rack_deleted(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate(max_weight=1000)
    section_output = await create_section(async_session, section_input)

    rack_input = RackInputSchemaFactory().generate(
        section_id=section_output.id, max_weight=500
    )
    rack_output = await create_rack(async_session, rack_input)

    section_object = await if_exists(Section, "id", section_output.id, async_session)

    assert section_object.reserved_weight == (
        section_output.reserved_weight + rack_input.max_weight
    )
    assert section_object.weight_to_reserve == (
        section_output.weight_to_reserve - rack_input.max_weight
    )

    await delete_single_rack(async_session, rack_output.id)
    section_object_with_no_racks = await if_exists(
        Section, "id", section_output.id, async_session
    )

    assert (
        section_object_with_no_racks.reserved_weight == section_output.reserved_weight
    )
    assert (
        section_object_with_no_racks.weight_to_reserve
        == section_output.weight_to_reserve
    )
