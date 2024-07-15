import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_levels.models import RackLevel
from src.apps.rack_levels.schemas import (
    RackLevelInputSchema,
    RackLevelOutputSchema,
    RackLevelUpdateSchema,
)
from src.apps.rack_levels.services import (
    create_rack_level,
    delete_single_rack_level,
    get_all_rack_levels,
    get_single_rack_level,
    manage_rack_level_state,
    update_single_rack_level,
)
from src.apps.racks.models import Rack
from src.apps.racks.schemas import RackInputSchema, RackOutputSchema, RackUpdateSchema
from src.apps.racks.services import create_rack, get_all_racks, get_single_rack
from src.apps.sections.models import Section
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.sections.services import create_section, get_single_section
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    NotEnoughRackResourcesException,
    RackLevelIsNotEmptyException,
    ServiceException,
    TooLittleRackLevelSlotsAmountException,
    TooLittleWeightAmountException,
    WeightLimitExceededException,
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
from tests.test_rack_levels.conftest import db_rack_levels
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
async def test_raise_exception_when_rack_level_created_with_nonexistent_level(
    async_session: AsyncSession,
):
    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=generate_uuid(), rack_level_number=5
    )

    with pytest.raises(DoesNotExist):
        await create_rack_level(async_session, rack_level_input)


@pytest.mark.asyncio
async def test_raise_exception_when_rack_does_not_have_slots_for_another_rack_level(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_object = await create_rack(async_session, rack_input)

    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_object.id, rack_level_number=1
    )
    await create_rack_level(async_session, rack_level_input_1)

    rack_input_level_2 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_object.id, rack_level_number=2
    )

    with pytest.raises(NotEnoughRackResourcesException):
        await create_rack_level(async_session, rack_input_level_2)


@pytest.mark.asyncio
async def test_raise_exception_when_there_is_no_available_weight_to_reserve_for_another_rack_level(
    async_session: AsyncSession, db_racks: PagedResponseSchema[RackOutputSchema]
):
    rack_input = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id,
        rack_level_number=db_racks.results[0].max_levels,
        max_weight=300000000000,
    )

    with pytest.raises(NotEnoughRackResourcesException):
        await create_rack_level(async_session, rack_input)


@pytest.mark.asyncio
async def test_raise_exception_when_pick_too_high_rack_level(
    async_session: AsyncSession, db_racks: PagedResponseSchema[RackOutputSchema]
):
    rack_input = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id,
        rack_level_number=db_racks.results[0].max_levels + 1,
        max_weight=3,
    )

    with pytest.raises(NotEnoughRackResourcesException):
        await create_rack_level(async_session, rack_input)


@pytest.mark.asyncio
async def test_raise_exception_when_rack_already_contains_rack_level_with_that_level_number(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack_input_level_1 = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id,
        rack_level_number=db_racks.results[0].max_levels,
        max_weight=3,
    )

    await create_rack_level(async_session, rack_input_level_1)

    rack_input_level_2 = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id,
        rack_level_number=db_racks.results[0].max_levels,
        max_weight=3,
    )

    with pytest.raises(AlreadyExists):
        await create_rack_level(async_session, rack_input_level_2)


@pytest.mark.asyncio
async def test_if_single_rack_level_is_returned(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_level = await get_single_rack_level(
        async_session, db_rack_levels.results[0].id
    )

    assert rack_level.id == db_rack_levels.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_when_getting_nonexistent_rack_level(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_rack_level(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_rack_levels_are_returned(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_levels = await get_all_rack_levels(async_session, PageParams())

    assert rack_levels.total == db_rack_levels.total


@pytest.mark.asyncio
async def test_raise_exception_when_rack_level_not_provided_when_managing_state(
    async_session: AsyncSession,
):
    with pytest.raises(ServiceException):
        await manage_rack_level_state()


@pytest.mark.asyncio
async def test_if_rack_level_max_slots_are_correctly_managed(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_level = await if_exists(
        RackLevel, "id", db_rack_levels.results[0].id, async_session
    )
    # decrement max_slots by 1
    rack_level = await manage_rack_level_state(rack_level, slots_involved=True)

    assert rack_level.available_slots == db_rack_levels.results[0].available_slots + 1
    assert rack_level.occupied_slots == db_rack_levels.results[0].occupied_slots - 1


@pytest.mark.asyncio
async def test_if_rack_level_weight_limits_are_correctly_managed(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_level = await if_exists(
        RackLevel, "id", db_rack_levels.results[0].id, async_session
    )
    # decrement max_weight by some weight
    weight = 100
    rack_level = await manage_rack_level_state(
        rack_level, weight_involved=True, stock_weight=weight
    )

    assert (
        rack_level.available_weight
        == db_rack_levels.results[0].available_weight + weight
    )
    assert (
        rack_level.occupied_weight == db_rack_levels.results[0].occupied_weight - weight
    )


@pytest.mark.asyncio
async def test_raise_exception_when_weight_is_not_provided_while_managing_weight_values(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_level = await if_exists(
        RackLevel, "id", db_rack_levels.results[0].id, async_session
    )
    with pytest.raises(ServiceException):
        await manage_rack_level_state(rack_level, weight_involved=True)


@pytest.mark.asyncio
async def test_if_rack_level_limits_are_correctly_managed_when_changing_max_weight_and_slots(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)

    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    new_max_weight = rack_level_object.max_weight - 40
    new_max_slots = rack_level_object.max_slots + 5

    updated_rack_level = await manage_rack_level_state(
        rack_level_object, max_weight=new_max_weight, max_slots=new_max_slots
    )

    assert updated_rack_level.available_slots == rack_level_output.available_slots + (
        new_max_slots - rack_level_output.max_slots
    )

    assert updated_rack_level.available_weight == rack_level_output.available_weight + (
        new_max_weight - rack_level_output.max_weight
    )


@pytest.mark.asyncio
async def test_raise_exception_when_updating_nonexistent_rack_level(
    async_session: AsyncSession,
):
    rack_level_input = RackLevelUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_rack_level(async_session, rack_level_input, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_new_max_weight_smaller_than_occupied_weight_amount_when_updating_rack_level(
    async_session: AsyncSession, db_sections: PagedResponseSchema[SectionOutputSchema]
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)

    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    rack_level_object.occupied_weight = 3
    async_session.add(rack_level_object)
    await async_session.commit()

    rack_level_input = RackLevelUpdateSchemaFactory().generate(max_weight=2)

    with pytest.raises(TooLittleWeightAmountException):
        await update_single_rack_level(
            async_session, rack_level_input, rack_level_object.id
        )


@pytest.mark.asyncio
async def test_raise_exception_while_updating_when_new_max_weight_bigger_than_max_weight_and_rack_weight_to_reserve_combined(
    async_session: AsyncSession, db_sections: PagedResponseSchema[SectionOutputSchema]
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_input = RackLevelUpdateSchemaFactory().generate(max_weight=100000100)

    with pytest.raises(WeightLimitExceededException):
        await update_single_rack_level(
            async_session, rack_level_input, rack_level_object.id
        )


@pytest.mark.asyncio
async def test_check_if_rack_state_managed_correctly_when_rack_level_max_weight_updated(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_before = await get_single_rack(async_session, rack_output.id)

    rack_level_input_2 = RackUpdateSchemaFactory().generate(max_weight=50)
    rack_level_output = await update_single_rack_level(
        async_session, rack_level_input_2, rack_level_object.id
    )
    rack_after = await get_single_rack(async_session, rack_output.id)

    assert rack_before.reserved_weight == rack_after.reserved_weight + (
        rack_level_input_1.max_weight - rack_level_input_2.max_weight
    )

    assert rack_before.weight_to_reserve == rack_after.weight_to_reserve - (
        rack_level_input_1.max_weight - rack_level_input_2.max_weight
    )


@pytest.mark.asyncio
async def test_raise_exception_when_new_max_slots_lower_than_occupied_slots(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id, rack_level_number=db_racks.results[0].max_levels
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_object.occupied_slots = 2
    async_session.add(rack_level_object)
    await async_session.commit()

    rack_level_input_2 = RackLevelUpdateSchemaFactory().generate(max_slots=1)
    with pytest.raises(TooLittleRackLevelSlotsAmountException):
        await update_single_rack_level(
            async_session, rack_level_input_2, rack_level_object.id
        )


@pytest.mark.asyncio
async def test_raise_exception_when_deleting_nonexistent_rack_level(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await delete_single_rack_level(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_deleting_rack_level_with_occupied_weight_or_slots(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id, rack_level_number=db_racks.results[0].max_levels
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_object.occupied_weight = 5
    async_session.add(rack_level_object)
    await async_session.commit()

    with pytest.raises(RackLevelIsNotEmptyException):
        await delete_single_rack_level(async_session, rack_level_object.id)

    rack_level_object.occupied_weight = 0
    rack_level_object.occupied_slots = 5
    async_session.add(rack_level_object)
    await async_session.commit()

    with pytest.raises(RackLevelIsNotEmptyException):
        await delete_single_rack_level(async_session, rack_level_object.id)


@pytest.mark.asyncio
async def test_check_if_rack_state_managed_correctly_when_rack_level_deleted(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_object = await if_exists(Rack, "id", rack_output.id, async_session)

    assert rack_object.reserved_weight == (
        rack_output.reserved_weight + rack_level_input.max_weight
    )
    assert rack_object.weight_to_reserve == (
        rack_output.weight_to_reserve - rack_level_input.max_weight
    )

    await delete_single_rack_level(async_session, rack_level_output.id)
    rack_object_with_no_rack_levels = await if_exists(
        Rack, "id", rack_output.id, async_session
    )

    assert (
        rack_object_with_no_rack_levels.reserved_weight == rack_output.reserved_weight
    )
    assert (
        rack_object_with_no_rack_levels.weight_to_reserve
        == rack_output.weight_to_reserve
    )


@pytest.mark.asyncio
async def test_check_if_rack_level_slots_are_created_correctly_when_creating_rack_level(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)

    assert rack_level_output.max_slots == len(rack_level_output.rack_level_slots)
    assert rack_level_output.max_slots == len(
        [slot for slot in rack_level_output.rack_level_slots if slot.is_active]
    )
