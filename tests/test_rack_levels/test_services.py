import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_level_slots.models import RackLevelSlot
from src.apps.rack_level_slots.schemas import RackLevelSlotOutputSchema
from src.apps.rack_levels.models import RackLevel
from src.apps.rack_levels.schemas import (
    RackLevelInputSchema,
    RackLevelOutputSchema,
    RackLevelUpdateSchema,
)
from src.apps.rack_levels.services import (
    add_single_stock_to_rack_level,
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
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas.stock_schemas import (
    StockOutputSchema,
    StockRackLevelInputSchema,
)
from src.apps.users.schemas import UserOutputSchema
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    CannotMoveIssuedStockException,
    DoesNotExist,
    NoAvailableRackLevelSlotException,
    NoAvailableSlotsInRackLevelException,
    NoAvailableWeightInRackLevelException,
    NotEnoughRackLevelResourcesException,
    NotEnoughRackResourcesException,
    RackLevelIsNotEmptyException,
    ServiceException,
    StockAlreadyInRackLevelException,
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
from tests.test_rack_level_slots.conftest import db_rack_level_slots
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
async def test_check_if_requested_rack_level_belongs_to_the_specified_rack(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_level = db_rack_levels.results[0]
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level.id, async_session
    )
    rack_level_output = await get_single_rack_level(
        async_session, rack_level_id=rack_level.id, rack_id=rack_level_object.rack_id
    )
    assert rack_level_output.rack_id == rack_level_output.rack_id


@pytest.mark.asyncio
async def test_if_multiple_rack_levels_are_returned(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_levels = await get_all_rack_levels(async_session, PageParams())

    assert rack_levels.total == db_rack_levels.total


@pytest.mark.asyncio
async def test_check_if_all_rack_levels_belongs_to_the_same_rack(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema]
):
    rack_levels = await get_all_rack_levels(
        async_session, PageParams(), rack_id=db_racks.results[0].id
    )
    
    assert {rack_level.rack_id for rack_level in rack_levels.results} == {db_racks.results[0].id}


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
async def test_if_rack_level_max_active_and_inactive_slots_are_manage_correctly(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
):
    rack_level = await if_exists(
        RackLevel, "id", db_rack_levels.results[0].id, async_session
    )
    # decrement active_slots by by 1
    rack_level = await manage_rack_level_state(rack_level, manage_active_slots=True)

    assert rack_level.available_slots == db_rack_levels.results[0].available_slots + 1
    assert rack_level.active_slots == db_rack_levels.results[0].active_slots + 1
    assert rack_level.inactive_slots == db_rack_levels.results[0].inactive_slots - 1


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
async def test_raise_exception_when_new_max_slots_amount_not_sufficient_for_active_slots_amount(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id,
        rack_level_number=db_racks.results[0].max_levels,
        max_slots=3,
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_object.active_slots = 2
    async_session.add(rack_level_object)
    await async_session.commit()

    rack_level_input_2 = RackLevelUpdateSchemaFactory().generate(max_slots=1)
    with pytest.raises(NotEnoughRackLevelResourcesException):
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


async def test_raise_exception_when_adding_stock_to_nonexistent_rack_level(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    stock_id_input = StockRackLevelInputSchema(id=db_stocks.results[0].id)
    with pytest.raises(DoesNotExist):
        await add_single_stock_to_rack_level(
            async_session, generate_uuid(), stock_id_input, db_staff_user.id
        )


async def test_raise_exception_when_adding_nonexistent_stock_to_rack_level(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    stock_id_input = StockRackLevelInputSchema(id=generate_uuid())
    with pytest.raises(DoesNotExist):
        await add_single_stock_to_rack_level(
            async_session,
            db_rack_levels.results[-1].id,
            stock_id_input,
            db_staff_user.id,
        )


async def test_raise_exception_when_adding_issued_stock_to_rack_level(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    issued_stocks = [stock for stock in db_stocks.results if stock.is_issued]
    stock_id_input = StockRackLevelInputSchema(id=issued_stocks[0].id)
    with pytest.raises(CannotMoveIssuedStockException):
        await add_single_stock_to_rack_level(
            async_session,
            db_rack_levels.results[-1].id,
            stock_id_input,
            db_staff_user.id,
        )


async def test_raise_exception_when_adding_the_stock_to_the_their_actual_rack_level(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=rack_output.max_levels
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    stock_object = await if_exists(Stock, "id", db_stocks.results[0].id, async_session)

    stock_id_input_1 = StockRackLevelInputSchema(id=db_stocks.results[0].id)
    await add_single_stock_to_rack_level(
        async_session, rack_level_object.id, stock_id_input_1, db_staff_user.id
    )
    await async_session.refresh(rack_level_object)
    await async_session.refresh(stock_object)

    with pytest.raises(StockAlreadyInRackLevelException):
        await add_single_stock_to_rack_level(
            async_session, rack_level_object.id, stock_id_input_1, db_staff_user.id
        )


async def test_raise_exception_when_rack_level_does_not_have_available_slots_when_adding_stock(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=rack_output.max_levels
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_object.available_slots = 0
    async_session.add(rack_level_object)
    await async_session.commit()

    stock_id_input = StockRackLevelInputSchema(id=db_stocks.results[0].id)
    with pytest.raises(NoAvailableSlotsInRackLevelException):
        await add_single_stock_to_rack_level(
            async_session, rack_level_object.id, stock_id_input, db_staff_user.id
        )


async def test_raise_exception_when_rack_level_does_not_have_available_weight_when_adding_stock(
    async_session: AsyncSession,
    db_racks: PagedResponseSchema[RackOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    stock = db_stocks.results[0]
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[-1].id,
        rack_level_number=db_racks.results[0].max_levels,
        max_weight=stock.weight,
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_object.available_weight = stock.weight - 1
    async_session.add(rack_level_object)
    await async_session.commit()

    stock_id_input = StockRackLevelInputSchema(id=stock.id)
    with pytest.raises(NoAvailableWeightInRackLevelException):
        await add_single_stock_to_rack_level(
            async_session, rack_level_object.id, stock_id_input, db_staff_user.id
        )


async def test_raise_exception_when_rack_level_does_not_have_matching_available_slots_for_a_new_stock(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    not_issued_stocks = [stock for stock in db_stocks.results if not stock.is_issued]

    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=rack_output.max_levels, max_slots=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)

    stock_1 = not_issued_stocks[0]
    stock_id_input_1 = StockRackLevelInputSchema(id=stock_1.id)
    await add_single_stock_to_rack_level(
        async_session, rack_level_output.id, stock_id_input_1, db_staff_user.id
    )

    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    rack_level_object.available_slots = 1  # bypass
    async_session.add(rack_level_object)
    await async_session.commit()

    stock_2 = not_issued_stocks[0]
    stock_id_input_2 = StockRackLevelInputSchema(id=stock_2.id)

    with pytest.raises(NoAvailableRackLevelSlotException):
        await add_single_stock_to_rack_level(
            async_session, rack_level_output.id, stock_id_input_2, db_staff_user.id
        )
