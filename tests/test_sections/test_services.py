import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.racks.schemas import RackOutputSchema
from src.apps.sections.models import Section
from src.apps.sections.schemas import (
    SectionInputSchema,
    SectionOutputSchema,
    SectionUpdateSchema,
)
from src.apps.sections.services import (
    create_section,
    delete_single_section,
    get_all_sections,
    get_single_section,
    manage_section_state,
    update_single_section,
)
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.stocks.services.stock_services import create_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.services import create_waiting_room
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.apps.warehouse.services import create_warehouse
from src.core.exceptions import (
    DoesNotExist,
    NotEnoughWarehouseResourcesException,
    SectionIsNotEmptyException,
    ServiceException,
    TooLittleRacksAmountException,
    TooLittleWeightAmountException,
    WarehouseDoesNotExistException,
)
from src.core.factory.section_factory import (
    SectionInputSchemaFactory,
    SectionUpdateSchemaFactory,
)
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
async def test_raise_exception_when_section_created_with_no_warehouse_object(
    async_session: AsyncSession,
):
    section_input = SectionInputSchemaFactory().generate()

    with pytest.raises(WarehouseDoesNotExistException):
        await create_section(async_session, section_input)


@pytest.mark.asyncio
async def test_raise_exception_when_there_is_no_space_for_new_sections_while_creating_one(
    async_session: AsyncSession,
):
    warehouse_input = WarehouseInputSchemaFactory().generate(max_sections=1)
    warehouse = await create_warehouse(async_session, warehouse_input)

    section_input_1 = SectionInputSchemaFactory().generate()
    section_1 = await create_section(async_session, section_input_1)

    section_input_2 = SectionInputSchemaFactory().generate()

    with pytest.raises(NotEnoughWarehouseResourcesException):
        await create_section(async_session, section_input_2)


@pytest.mark.asyncio
async def test_if_single_section_is_returned(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    section = await get_single_section(async_session, db_sections.results[0].id)

    assert section.id == db_sections.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_when_getting_nonexistent_section(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_section(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_sections_are_returned(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    sections = await get_all_sections(async_session, PageParams())

    assert sections.total == db_sections.total


@pytest.mark.asyncio
async def test_raise_exception_when_section_not_provided_when_managing_state(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    with pytest.raises(ServiceException):
        await manage_section_state()


@pytest.mark.asyncio
async def test_if_section_racks_limits_are_correctly_managed(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    section = await if_exists(Section, "id", db_sections.results[0].id, async_session)
    # decrement max_racks by 1
    section = await manage_section_state(section, racks_involved=True)

    assert section.available_racks == db_sections.results[0].available_racks + 1


@pytest.mark.asyncio
async def test_if_section_weight_limits_are_correctly_managed(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    section = await if_exists(Section, "id", db_sections.results[0].id, async_session)
    # decrement max_weight by stock_weight
    stock_weight = 100
    section = await manage_section_state(
        section, weight_involved=True, stock_weight=stock_weight
    )

    assert (
        section.available_weight
        == db_sections.results[0].available_weight + stock_weight
    )


@pytest.mark.asyncio
async def test_raise_exception_when_stock_weight_is_not_provided(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    section = await if_exists(Section, "id", db_sections.results[0].id, async_session)
    with pytest.raises(ServiceException):
        await manage_section_state(section, weight_involved=True)


@pytest.mark.asyncio
async def test_if_section_limits_are_correctly_managed_when_changing_max_weight_and_racks(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate()
    section_output = await create_section(async_session, section_input)

    section = await if_exists(Section, "id", section_output.id, async_session)
    new_max_weight = 9999
    new_max_racks = 35

    updated_section = await manage_section_state(
        section, max_weight=new_max_weight, max_racks=new_max_racks
    )

    assert updated_section.available_racks == section_output.available_racks + (
        new_max_racks - section_output.max_racks
    )

    assert updated_section.available_weight == section_output.available_weight + (
        new_max_weight - section_output.max_weight
    )

    assert updated_section.weight_to_reserve == section.weight_to_reserve


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
    )


@pytest.mark.asyncio
async def test_raise_exception_when_updating_nonexistent_section(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    section_input = SectionUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_section(async_session, section_input, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_new_max_weight_smaller_than_occupied_weight_amount(
    async_session: AsyncSession,
):
    warehouse_input = WarehouseInputSchemaFactory().generate(max_sections=1)
    warehouse = await create_warehouse(async_session, warehouse_input)

    section_input = SectionInputSchemaFactory().generate()
    section = await create_section(async_session, section_input)

    section = await if_exists(Section, "id", section.id, async_session)
    section.occupied_weight = 3
    async_session.add(section)
    await async_session.commit()

    section_input = SectionUpdateSchemaFactory().generate(max_weight=2)

    with pytest.raises(TooLittleWeightAmountException):
        await update_single_section(async_session, section_input, section.id)


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
        await update_single_section(async_session, section_input, section.id)


@pytest.mark.asyncio
async def test_raise_exception_when_new_max_racks_smaller_than_occupied_racks_amount(
    async_session: AsyncSession,
):
    warehouse_input = WarehouseInputSchemaFactory().generate(max_sections=1)
    warehouse = await create_warehouse(async_session, warehouse_input)

    section_input = SectionInputSchemaFactory().generate()
    section = await create_section(async_session, section_input)

    section = await if_exists(Section, "id", section.id, async_session)
    section.occupied_racks = 3
    async_session.add(section)
    await async_session.commit()

    section_input = SectionUpdateSchemaFactory().generate(max_racks=2)

    with pytest.raises(TooLittleRacksAmountException):
        await update_single_section(async_session, section_input, section.id)


@pytest.mark.asyncio
async def test_raise_exception_when_deleting_nonexistent_section(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await delete_single_section(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_deleting_section_with_occupied_racks(
    async_session: AsyncSession, db_sections: PagedResponseSchema[SectionOutputSchema]
):
    with pytest.raises(SectionIsNotEmptyException):
        await delete_single_section(async_session, db_sections.results[0].id)


@pytest.mark.asyncio
async def test_raise_exception_when_deleting_section_with_positive_occupied_or_reserved_weight(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    section_input = SectionInputSchemaFactory().generate()
    section = await create_section(async_session, section_input)

    section_object = await if_exists(Section, "id", section.id, async_session)
    section_object.reserved_weight = 10
    async_session.add(section_object)

    await async_session.commit()

    with pytest.raises(SectionIsNotEmptyException):
        await delete_single_section(async_session, section_object.id)
