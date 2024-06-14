from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.warehouse.models import Warehouse
from src.apps.warehouse.schemas import (
    WarehouseInputSchema,
    WarehouseOutputSchema,
    WarehouseBaseOutputSchema,
    WarehouseUpdateSchema
)
from src.core.exceptions import (
    AlreadyExists, DoesNotExist, IsOccupied,
    WarehouseAlreadyExistsException,
    TooLittleSectionAmountException,
    TooLittleWaitingRoomAmountException,
    WarehouseIsNotEmptyException,
    WarehouseAlreadyExistsException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_warehouse(
    session: AsyncSession, warehouse_input: WarehouseInputSchema
) -> WarehouseOutputSchema:
    warehouse_data = warehouse_input.dict()

    warehouses = await get_all_warehouses(session, PageParams())
    if warehouses.total:
        raise WarehouseAlreadyExistsException

    new_warehouse = Warehouse(**warehouse_data)
    session.add(new_warehouse)
    await session.commit()

    return WarehouseOutputSchema.from_orm(new_warehouse)


async def get_single_warehouse(
    session: AsyncSession, warehouse_id: str
) -> WarehouseOutputSchema:
    if not (warehouse_object := await if_exists(Warehouse, "id", warehouse_id, session)):
        raise DoesNotExist(Warehouse.__name__, "id", warehouse_id)

    return WarehouseOutputSchema.from_orm(warehouse_object)


async def get_all_warehouses(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[WarehouseBaseOutputSchema]:
    query = select(Warehouse)

    return await paginate(
        query=query,
        response_schema=WarehouseBaseOutputSchema,
        table=Warehouse,
        page_params=page_params,
        session=session,
    )
    
async def manage_warehouse_state(
    warehouse_object: Warehouse,
    max_sections: Decimal = None,
    max_waiting_rooms: int = None,
    adding_resources_to_warehouse: bool = True,
    sections_involved: bool = None,
    waiting_rooms_involved: bool = None
) -> Warehouse:
    if warehouse_object is None:
        raise ServiceException("Warehouse object was not provided! ")
    multiplier = 1 if adding_resources_to_warehouse else -1
    if sections_involved:
        warehouse_object.available_sections -= multiplier
        warehouse_object.occupied_sections += multiplier
    if waiting_rooms_involved:
        warehouse_object.available_waiting_rooms -= multiplier
        warehouse_object.occupied_waiting_rooms += multiplier
        
    if max_sections is not None:
        new_available_sections = max_sections - warehouse_object.occupied_sections
        warehouse_object.available_sections = new_available_sections
    if max_waiting_rooms is not None:
        new_available_waiting_rooms = max_waiting_rooms - warehouse_object.occupied_waiting_rooms
        warehouse_object.available_waiting_rooms = new_available_waiting_rooms

    return warehouse_object
    
    
async def update_single_warehouse(
    session: AsyncSession, warehouse_input: WarehouseUpdateSchema, warehouse_id: str
) -> WarehouseOutputSchema:
    if not (warehouse_object := await if_exists(Warehouse, "id", warehouse_id, session)):
        raise DoesNotExist(Warehouse.__name__, "id", warehouse_id)

    warehouse_data = warehouse_input.dict(exclude_unset=True)

    if new_max_sections := warehouse_data.get("max_sections"):
        if new_max_sections < warehouse_object.occupied_sections:
            raise TooLittleSectionAmountException(
                new_max_sections, warehouse_object.occupied_sections
            )

    if new_max_waiting_rooms := warehouse_data.get("max_waiting_rooms"):
        if new_max_waiting_rooms < warehouse_object.occupied_waiting_rooms:
            raise TooLittleWaitingRoomAmountException(
                new_max_waiting_rooms, warehouse_object.occupied_waiting_rooms
            )
            
    warehouse_object = await manage_warehouse_state(
        warehouse_object, new_max_sections, new_max_waiting_rooms
    )
    session.add(warehouse_object)
    
    if warehouse_data:
        statement = (
            update(Warehouse).filter(Warehouse.id == warehouse_id).values(**warehouse_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(warehouse_object)

    return await get_single_warehouse(session, warehouse_id=warehouse_id)


async def delete_single_warehouse(session: AsyncSession, warehouse_id: str):
    if not (
        warehouse_object := await if_exists(
            Warehouse, "id", warehouse_id, session
        )
    ):
        raise DoesNotExist(Warehouse.__name__, "id", warehouse_id)

    if warehouse_object.sections:
        raise WarehouseIsNotEmptyException(resource="sections")
    
    if warehouse_object.waiting_rooms:
        raise WarehouseIsNotEmptyException(resource="waiting rooms")
    
    statement = delete(Warehouse).filter(Warehouse.id == warehouse_id)
    result = await session.execute(statement)
    await session.commit()

    return result


