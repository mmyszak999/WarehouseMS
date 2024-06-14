from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sections.models import Section
from src.apps.sections.schemas import (
    SectionInputSchema,
    SectionOutputSchema,
    SectionBaseOutputSchema,
    SectionUpdateSchema
)
from src.core.exceptions import (
    AlreadyExists, DoesNotExist, IsOccupied,
    WarehouseAlreadyExistsException,
    WarehouseDoesNotExistException,
    SectionIsNotEmptyException
)
from src.apps.warehouse.services import get_all_warehouses
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_section(
    session: AsyncSession, section_input: SectionInputSchema
) -> SectionOutputSchema:
    section_data = section_input.dict()

    warehouses = await get_all_warehouses(session, PageParams())
    if not warehouses.total:
        raise WarehouseDoesNotExistException

    new_section = Section(**section_data)
    session.add(new_section)
    await session.commit()

    return SectionOutputSchema.from_orm(new_section)


async def get_single_section(
    session: AsyncSession, section_id: str
) -> SectionOutputSchema:
    if not (section_object := await if_exists(Section, "id", section_id, session)):
        raise DoesNotExist(Section.__name__, "id", section_id)

    return SectionOutputSchema.from_orm(section_object)


async def get_all_sections(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[SectionBaseOutputSchema]:
    query = select(Section)

    return await paginate(
        query=query,
        response_schema=SectionBaseOutputSchema,
        table=Section,
        page_params=page_params,
        session=session,
    )
    
async def manage_section_state(
    section_object: Section,
    max_weight: Decimal = None,
    max_racks: int = None,
    adding_resources_to_section: bool = True,
    racks_involved: bool = None,
    weight_involved: bool = None,
    stock_weight: Decimal = None
) -> Section:
    if section_object is None:
        raise ServiceException("Section object was not provided! ")
    
    multiplier = 1 if adding_resources_to_section else -1
    if racks_involved:
        section_object.available_racks -= multiplier
        section_object.occupied_racks += multiplier
    
    if weight_involved:
        section_object.available_weight -= multiplier * stock_weight
        section_object.occupied_weight += multiplier * stock_weight

    if max_weight is not None:
        new_available_weight = max_weight - section_object.occupied_weight
        section_object.available_weight = new_available_weight
    if max_racks is not None:
        new_available_racks = max_racks- section_object.occupied_racks
        section_object.available_racks = new_available_racks

    return section_object
    
    
async def update_single_section(
    session: AsyncSession, section_input: SectionUpdateSchema, section_id: str
) -> SectionOutputSchema:
    if not (section_object := await if_exists(Section, "id", section_id, session)):
        raise DoesNotExist(Section.__name__, "id", section_id)

    section_data = section_input.dict(exclude_unset=True)

    if new_max_sections := section_data.get("max_sections"):
        if new_max_sections < section_object.occupied_sections:
            raise TooLittleSectionAmountException(
                new_max_sections, section_object.occupied_sections
            )

    if new_max_waiting_rooms := section_data.get("max_waiting_rooms"):
        if new_max_waiting_rooms < section_object.occupied_waiting_rooms:
            raise TooLittleWaitingRoomAmountException(
                new_max_waiting_rooms, section_object.occupied_waiting_rooms
            )
            
    section_object = await manage_section_state(
        section_object, new_max_sections, new_max_waiting_rooms
    )
    session.add(section_object)
    
    if section_data:
        statement = (
            update(Section).filter(Section.id == section_id).values(**section_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(section_object)

    return await get_single_section(session, section_id=section_id)


async def delete_single_section(session: AsyncSession, section_id: str):
    if not (
        section_object := await if_exists(
            Section, "id", section_id, session
        )
    ):
        raise DoesNotExist(Section.__name__, "id", section_id)

    if section_object.racks:
        raise SectionIsNotEmptyException(resource="sections")
    
    statement = delete(Section).filter(Section.id == section_id)
    result = await session.execute(statement)
    await session.commit()

    return result


