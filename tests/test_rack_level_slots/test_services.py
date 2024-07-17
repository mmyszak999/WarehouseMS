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
from src.apps.rack_level_slots.services import (
    add_single_stock_to_rack_level_slot,
    create_rack_level_slot,
    get_all_rack_level_slots,   
    get_single_rack_level_slot,
    update_single_rack_level_slot,
    manage_single_rack_level_slot_state,
    manage_rack_level_slots_when_changing_rack_level_max_slots
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
    StockRackLevelSlotInputSchema,
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
    RackLevelSlotIsNotEmptyException,
    CantActivateRackLevelSlotException,
    CantDeactivateRackLevelSlotException,
    TooSmallInactiveSlotsQuantityException,
    ExistingGapBetweenInactiveSlotsToDeleteException
)
from src.core.factory.rack_factory import (
    RackInputSchemaFactory,
    RackUpdateSchemaFactory,
)
from src.core.factory.rack_level_factory import (
    RackLevelInputSchemaFactory,
    RackLevelUpdateSchemaFactory,
)
from src.core.factory.rack_level_slot_factory import (
    RackLevelSlotInputSchemaFactory,
    RackLevelSlotUpdateSchemaFactory,
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
async def test_raise_exception_when_rack_level_slot_created_with_nonexistent_rack_level(
    async_session: AsyncSession,
):
    rack_level_slot_input = RackLevelSlotInputSchemaFactory().generate(
        rack_level_id=generate_uuid(), rack_level_slot_number=1
    )

    with pytest.raises(DoesNotExist):
        await create_rack_level_slot(async_session, rack_level_slot_input, creating_rack_level=True)


async def test_raise_exception_when_rack_level_does_not_have_available_slots_when_creating_rack_level(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)
    
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id,
        rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_object.available_slots = 0
    async_session.add(rack_level_object)
    await async_session.commit()

    rack_level_slot_input = RackLevelSlotInputSchemaFactory().generate(
        rack_level_id=rack_level_object.id, rack_level_slot_number=1
    )
    with pytest.raises(NotEnoughRackLevelResourcesException):
        await create_rack_level_slot(
            async_session, rack_level_slot_input, creating_rack_level=True
        )


async def test_raise_exception_when_new_slot_got_too_high_rack_level_slot_number(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)
    
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id,
        rack_level_number=1,
        max_slots=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_slot_object = await if_exists(
        RackLevelSlot, "id", rack_level_output.rack_level_slots[0].id, async_session
    )

    rack_level_slot_input = RackLevelSlotInputSchemaFactory().generate(
        rack_level_id=rack_level_output.id, rack_level_slot_number=2
    )
    with pytest.raises(NotEnoughRackLevelResourcesException):
        await create_rack_level_slot(
            async_session, rack_level_slot_input, creating_rack_level=True
        )


async def test_raise_exception_when_creating_slot_with_existing_number_on_the_rack_level(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)
    
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id,
        rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_slot_object = await if_exists(
        RackLevelSlot, "id", rack_level_output.rack_level_slots[0].id, async_session
    )

    rack_level_slot_input = RackLevelSlotInputSchemaFactory().generate(
        rack_level_id=rack_level_output.id, rack_level_slot_number=1
    )
    with pytest.raises(AlreadyExists):
        await create_rack_level_slot(
            async_session, rack_level_slot_input, creating_rack_level=True
        )

@pytest.mark.asyncio
async def test_if_single_rack_level_slot_is_returned(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
):
    rack_level_slot = await get_single_rack_level_slot(
        async_session, db_rack_level_slots.results[0].id
    )

    assert rack_level_slot.id == db_rack_level_slots.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_when_getting_nonexistent_rack_level_slot(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_rack_level_slot(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_rack_level_slots_are_returned(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
):
    rack_level_slots = await get_all_rack_level_slots(async_session, PageParams())

    assert rack_level_slots.total == db_rack_level_slots.total
    
    
@pytest.mark.asyncio
async def test_raise_exception_when_updating_nonexistent_rack_level_slot(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema]
):
    rack_level_slot_input = RackLevelSlotUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_rack_level_slot(async_session, rack_level_slot_input, generate_uuid())


async def test_raise_exception_when_managing_state_of_nonexistent_rack_level_slot(
    async_session: AsyncSession,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await manage_single_rack_level_slot_state(async_session, generate_uuid(), activate_slot=True)


async def test_raise_exception_when_managing_state_of_occupied_slot(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_level_slots = await get_all_rack_level_slots(
        async_session, PageParams(), output_schema=RackLevelSlotOutputSchema
    )
    occupied_slots = [slot for slot in rack_level_slots.results if slot.stock]
    with pytest.raises(RackLevelSlotIsNotEmptyException):
        await manage_single_rack_level_slot_state(async_session, occupied_slots[0].id, activate_slot=True)


async def test_raise_exception_when_activating_activated_slot(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    available_slots = [slot for slot in db_rack_level_slots.results if not slot.stock]
    
    with pytest.raises(CantActivateRackLevelSlotException):
        await manage_single_rack_level_slot_state(async_session, available_slots[0].id, activate_slot=True)


async def test_raise_exception_when_deactivating_deactivated_slot(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)
    
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id,
        rack_level_number=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_slot_object = await if_exists(
        RackLevelSlot, "id", rack_level_output.rack_level_slots[0].id, async_session
    )
    
    rack_level_slot_object.is_active = False
    async_session.add(rack_level_slot_object)
    await async_session.commit()
    await async_session.refresh(rack_level_slot_object)
    
    with pytest.raises(CantDeactivateRackLevelSlotException):
        await manage_single_rack_level_slot_state(async_session, rack_level_slot_object.id, activate_slot=False)


async def test_check_if_rack_level_state_is_managed_correctly_when_changing_rack_level_slot_state(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_level_output = db_rack_levels.results[0]
    available_slots = [slot for slot in rack_level_output.rack_level_slots if not slot.stock]
    
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    
    await manage_single_rack_level_slot_state(
        async_session, available_slots[0].id, activate_slot=False
    )
    
    await async_session.refresh(rack_level_object)
    
    assert rack_level_object.active_slots == rack_level_output.active_slots - 1
    assert rack_level_object.available_slots == rack_level_output.available_slots - 1
    assert rack_level_object.inactive_slots == rack_level_output.inactive_slots + 1


async def test_check_if_rack_level_have_slots_created_when_max_slots_increases(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_level_output = db_rack_levels.results[0]
    
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    
    max_slots_difference=2
    await manage_rack_level_slots_when_changing_rack_level_max_slots(
        async_session, rack_level_object,
        max_slots_difference=max_slots_difference, creating_slots=True
    )
    
    await async_session.refresh(rack_level_object)
    
    assert len(rack_level_object.rack_level_slots) == len(rack_level_output.rack_level_slots) + max_slots_difference


async def test_check_if_rack_level_have_slots_created_when_max_slots_decreased(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_level_output = db_rack_levels.results[0]
    
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    rack_level_object.rack_level_slots[-1].is_active=False
    async_session.add(rack_level_object)
    await async_session.commit()
    await async_session.refresh(rack_level_object)
    
    max_slots_difference=-1
    await manage_rack_level_slots_when_changing_rack_level_max_slots(
        async_session, rack_level_object,
        max_slots_difference=max_slots_difference, creating_slots=False
    )
    
    await async_session.refresh(rack_level_object)
    assert len(rack_level_object.rack_level_slots) == len(rack_level_output.rack_level_slots) + max_slots_difference
    assert rack_level_object.inactive_slots == rack_level_output - max_slots_difference


async def test_raise_exception_when_rack_level_does_not_have_enough_inactive_slots_to_delete(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_level_output = db_rack_levels.results[0]
    
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    
    max_slots_difference=-1
    
    with pytest.raises(TooSmallInactiveSlotsQuantityException):
        await manage_rack_level_slots_when_changing_rack_level_max_slots(
            async_session, rack_level_object,
            max_slots_difference=max_slots_difference, creating_slots=False
        )

async def test_check_if_rack_level_have_slots_created_when_max_slots_decreased(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    rack_level_output = db_rack_levels.results[0]
    
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    rack_level_object.rack_level_slots[0].is_active=False
    async_session.add(rack_level_object)
    await async_session.commit()
    await async_session.refresh(rack_level_object)
    
    max_slots_difference=-1
    
    with pytest.raises(ExistingGapBetweenInactiveSlotsToDeleteException):
        await manage_rack_level_slots_when_changing_rack_level_max_slots(
            async_session, rack_level_object,
            max_slots_difference=max_slots_difference, creating_slots=False
        )
    
    
"""d
"""

async def test_raise_exception_when_adding_stock_to_nonexistent_rack_level_slot(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    stock_id_input = StockRackLevelSlotInputSchema(id=db_stocks.results[0].id)
    with pytest.raises(DoesNotExist):
        await add_single_stock_to_rack_level_slot(
            async_session, generate_uuid(), stock_id_input, db_staff_user.id
        )


async def test_raise_exception_when_adding_nonexistent_stock_to_rack_level_slot(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    stock_id_input = StockRackLevelSlotInputSchema(id=generate_uuid())
    with pytest.raises(DoesNotExist):
        await add_single_stock_to_rack_level_slot(
            async_session,
            db_rack_level_slots.results[-1].id,
            stock_id_input,
            db_staff_user.id,
        )


async def test_raise_exception_when_adding_issued_stock_to_rack_level(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    issued_stocks = [stock for stock in db_stocks.results if stock.is_issued]
    stock_id_input = StockRackLevelSlotInputSchema(id=issued_stocks[0].id)
    with pytest.raises(CannotMoveIssuedStockException):
        await add_single_stock_to_rack_level_slot(
            async_session,
            db_rack_level_slots.results[-1].id,
            stock_id_input,
            db_staff_user.id,
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

    stock_id_input = StockRackLevelSlotInputSchema(id=db_stocks.results[0].id)
    with pytest.raises(NoAvailableSlotsInRackLevelException):
        await add_single_stock_to_rack_level(
            async_session, rack_level_object.id, stock_id_input, db_staff_user.id
        )


async def test_raise_exception_when_rack_level_does_not_have_available_weight_when_adding_stock(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: PagedResponseSchema[UserOutputSchema],
):
    stock = db_stocks.results[0]
    rack_input = RackInputSchemaFactory().generate(
        section_id=db_sections.results[0].id, max_levels=1
    )
    rack_output = await create_rack(async_session, rack_input)
    
    rack_level_input_1 = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id,
        rack_level_number=rack_output.max_levels,
        max_weight=stock.weight,
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input_1)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    rack_level_object.available_weight = stock.weight - 1
    async_session.add(rack_level_object)
    await async_session.commit()

    stock_id_input = StockRackLevelSlotInputSchema(id=stock.id)
    with pytest.raises(NoAvailableWeightInRackLevelException):
        await add_single_stock_to_rack_level(
            async_session, rack_level_object.id, stock_id_input, db_staff_user.id
        )