import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.stocks.schemas.stock_schemas import (
    StockOutputSchema,
)
from src.apps.stocks.services.stock_services import create_stocks
from src.apps.users.schemas import UserOutputSchema
from src.apps.warehouse.models import Warehouse
from src.apps.warehouse.schemas import (
    WarehouseInputSchema,
    WarehouseOutputSchema,
    WarehouseUpdateSchema,
)
from src.apps.warehouse.services import (
    create_warehouse,
    delete_single_warehouse,
    get_single_warehouse,
    manage_warehouse_state,
    update_single_warehouse,
)
from src.core.factory.waiting_room_factory import (
    WaitingRoomInputSchemaFactory,
)
from src.apps.waiting_rooms.services import (
    create_waiting_room
)
from src.core.exceptions import (
    DoesNotExist,
    WarehouseAlreadyExistsException,
    ServiceException,
    TooLittleSectionAmountException,
    TooLittleSectionAmountException,
    WarehouseIsNotEmptyException
)
from src.apps.sections.services import (
    create_section
)
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.core.factory.warehouse_factory import (
    WarehouseInputSchemaFactory,
    WarehouseUpdateSchemaFactory,
)
from src.core.factory.section_factory import (
    SectionInputSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import db_categories, db_products
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_warehouse.conftest import db_warehouse


@pytest.mark.asyncio
async def test_raise_exception_when_another_warehouse_is_requested_to_be_created(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    warehouse_input = WarehouseInputSchemaFactory().generate()

    with pytest.raises(WarehouseAlreadyExistsException):
        await create_warehouse(async_session, warehouse_input)


@pytest.mark.asyncio
async def test_if_single_warehouse_is_returned(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    warehouse = await get_single_warehouse(async_session, db_warehouse.results[0].id)
    
    assert warehouse.id == db_warehouse.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_when_getting_nonexistent_warehouse(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_warehouse(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_when_warehouse_not_provided_when_managing_state(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    with pytest.raises(ServiceException):
        await manage_warehouse_state()


@pytest.mark.asyncio
async def test_if_warehouse_section_limits_are_correctly_managed(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    warehouse = await if_exists(Warehouse, "id", db_warehouse.results[0].id, async_session)
    #decrement max_section by 1
    warehouse = await manage_warehouse_state(warehouse, sections_involved=True)
    
    assert warehouse.available_sections == db_warehouse.results[0].available_sections + 1


@pytest.mark.asyncio
async def test_if_warehouse_sections_limits_are_correctly_managed(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    warehouse = await if_exists(Warehouse, "id", db_warehouse.results[0].id, async_session)
    #decrement max_sections by 1
    warehouse = await manage_warehouse_state(warehouse, sections_involved=True)
    
    assert warehouse.available_sections == db_warehouse.results[0].available_sections + 1


@pytest.mark.asyncio
async def test_if_warehouse_limits_are_correctly_managed_when_changing_max_sections_and_sections(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    warehouse = await if_exists(Warehouse, "id", db_warehouse.results[0].id, async_session)
    new_max_sections = 55
    new_max_waiting_rooms = 44
    warehouse = await manage_warehouse_state(
        warehouse, max_sections=new_max_sections, max_waiting_rooms=new_max_waiting_rooms
    )
    
    assert warehouse.available_sections == db_warehouse.results[0].available_sections + (
        new_max_sections - db_warehouse.results[0].max_sections
    )
    
    assert warehouse.available_waiting_rooms == db_warehouse.results[0].available_waiting_rooms + (
        new_max_waiting_rooms - db_warehouse.results[0].max_waiting_rooms
    )

@pytest.mark.asyncio
async def test_raise_exception_when_updating_nonexistent_warehouse(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    warehouse_input = WarehouseUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_warehouse(
            async_session,
            warehouse_input,
            generate_uuid()
        )

@pytest.mark.asyncio
async def test_raise_when_new_max_sections_smaller_than_occupied_sections_amount(
    async_session: AsyncSession
):
    warehouse_input = WarehouseInputSchemaFactory().generate(max_sections=2)
    warehouse = await create_warehouse(async_session, warehouse_input)
    
    section_input_1 = SectionInputSchemaFactory().generate()
    section_1 = await create_section(
        async_session, section_input_1
    )
    
    section_input_2 = SectionInputSchemaFactory().generate()
    section_2 = await create_section(
        async_session, section_input_2
    )
    
    warehouse_input = WarehouseUpdateSchemaFactory().generate(max_sections=1)
    
    with pytest.raises(TooLittleSectionAmountException):
        await update_single_warehouse(
            async_session,
            warehouse_input,
            warehouse.id
        )

@pytest.mark.asyncio
async def test_raise_when_new_max_sections_smaller_than_occupied_sections_amount(
    async_session: AsyncSession
):
    warehouse_input = WarehouseInputSchemaFactory().generate(max_sections=2)
    warehouse = await create_warehouse(async_session, warehouse_input)
    
    section_input_1 = SectionInputSchemaFactory().generate()
    section_1 = await create_section(
        async_session, section_input_1
    )
    
    section_input_2 = SectionInputSchemaFactory().generate()
    section_2 = await create_section(
        async_session, section_input_2
    )
    
    warehouse = await if_exists(Warehouse, "id", warehouse.id, async_session)
    
    warehouse_input = WarehouseUpdateSchemaFactory().generate(max_sections=1)
    
    with pytest.raises(TooLittleSectionAmountException):
        await update_single_warehouse(
            async_session,
            warehouse_input,
            warehouse.id
        )
        

@pytest.mark.asyncio
async def test_raise_exception_when_deleting_nonexistent_warehouse(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await delete_single_warehouse(
            async_session,
            generate_uuid()
        )


@pytest.mark.asyncio
async def test_raise_when_deleting_warehouse_with_occupied_sections(
    async_session: AsyncSession
):
    warehouse_input = WarehouseInputSchemaFactory().generate()
    warehouse = await create_warehouse(async_session, warehouse_input)
    
    section_input_1 = SectionInputSchemaFactory().generate()
    section_1 = await create_section(
        async_session, section_input_1
    )
    
    with pytest.raises(WarehouseIsNotEmptyException):
        await delete_single_warehouse(
            async_session,
            warehouse.id
        )


@pytest.mark.asyncio
async def test_raise_when_deleting_warehouse_with_occupied_waiting_rooms(
    async_session: AsyncSession
):
    warehouse_input = WarehouseInputSchemaFactory().generate()
    warehouse = await create_warehouse(async_session, warehouse_input)
    
    waiting_room_input = WaitingRoomInputSchemaFactory().generate()
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input
    )
    
    with pytest.raises(WarehouseIsNotEmptyException):
        await delete_single_warehouse(
            async_session,
            warehouse.id
        )