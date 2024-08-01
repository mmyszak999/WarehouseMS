from decimal import Decimal
from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sections.models import Section
from src.apps.sections.schemas import (
    SectionBaseOutputSchema,
    SectionInputSchema,
    SectionOutputSchema,
    SectionUpdateSchema,
)
from src.apps.warehouse.models import Warehouse
from src.apps.warehouse.services import get_all_warehouses, manage_warehouse_state
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    NotEnoughWarehouseResourcesException,
    SectionIsNotEmptyException,
    ServiceException,
    TooLittleRackLevelsAmountException,
    TooLittleRacksAmountException,
    TooLittleWeightAmountException,
    WarehouseAlreadyExistsException,
    WarehouseDoesNotExistException,
    WeightLimitExceededException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def create_section(
    session: AsyncSession, section_input: SectionInputSchema
) -> SectionOutputSchema:
    section_data = section_input.dict()

    warehouses = await get_all_warehouses(session, PageParams())
    if not warehouses.total:
        raise WarehouseDoesNotExistException

    warehouse = await if_exists(Warehouse, "id", warehouses.results[0].id, session)
    if not warehouse.available_sections:
        raise NotEnoughWarehouseResourcesException(resource="sections")

    section_data["warehouse_id"] = warehouse.id

    new_section = Section(**section_data)
    session.add(new_section)

    await manage_warehouse_state(
        warehouse, adding_resources_to_warehouse=False, sections_involved=True
    )
    session.add(warehouse)
    await session.commit()

    return SectionBaseOutputSchema.from_orm(new_section)


async def get_single_section(
    session: AsyncSession,
    section_id: str,
    output_schema: BaseModel = SectionOutputSchema,
) -> Union[SectionOutputSchema, SectionBaseOutputSchema]:
    if not (section_object := await if_exists(Section, "id", section_id, session)):
        raise DoesNotExist(Section.__name__, "id", section_id)

    return output_schema.from_orm(section_object)


async def get_all_sections(
    session: AsyncSession,
    page_params: PageParams,
    output_schema: BaseModel = SectionBaseOutputSchema,
    query_params: list[tuple] = None,
) -> Union[
    PagedResponseSchema[SectionOutputSchema],
    PagedResponseSchema[SectionBaseOutputSchema],
]:
    query = select(Section)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Section)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=Section,
        page_params=page_params,
        session=session,
    )


async def manage_section_state(
    section_object: Section = None,
    max_weight: Decimal = None,
    max_racks: int = None,
    adding_resources_to_section: bool = True,
    racks_involved: bool = None,
    weight_involved: bool = None,
    stock_weight: Decimal = None,
    reserved_weight_involved: bool = None,
) -> Section:
    if not (isinstance(section_object, Section)):
        raise ServiceException("Section object was not provided! ")

    multiplier = -1 if adding_resources_to_section else 1

    if weight_involved:
        if stock_weight is None:
            raise ServiceException("Stock weight was not provided! ")
        section_object.available_weight -= multiplier * stock_weight
        section_object.occupied_weight += multiplier * stock_weight

    if reserved_weight_involved:
        if stock_weight is None:
            raise ServiceException("Stock weight was not provided! ")
        section_object.weight_to_reserve -= multiplier * stock_weight
        section_object.reserved_weight += multiplier * stock_weight

    if racks_involved:
        section_object.available_racks -= multiplier
        section_object.occupied_racks += multiplier

    if max_weight is not None:
        new_available_weight = max_weight - section_object.occupied_weight
        section_object.available_weight = new_available_weight

        if stock_weight is not None:
            section_object.weight_to_reserve += stock_weight * multiplier
            section_object.reserved_weight -= stock_weight * multiplier
        else:
            new_weight_to_reserve = max_weight - section_object.reserved_weight
            section_object.weight_to_reserve = new_weight_to_reserve

    if max_racks is not None:
        new_available_racks = max_racks - section_object.occupied_racks
        section_object.available_racks = new_available_racks

    return section_object


async def update_single_section(
    session: AsyncSession, section_input: SectionUpdateSchema, section_id: str
) -> SectionOutputSchema:
    if not (section_object := await if_exists(Section, "id", section_id, session)):
        raise DoesNotExist(Section.__name__, "id", section_id)

    section_data = section_input.dict(exclude_unset=True, exclude_none=True)

    if new_max_weight := section_data.get("max_weight"):
        if new_max_weight < section_object.occupied_weight:
            raise TooLittleWeightAmountException(
                new_max_weight, section_object.occupied_weight, Section.__name__
            )

        if new_max_weight < section_object.reserved_weight:
            raise TooLittleWeightAmountException(
                new_max_weight, section_object.reserved_weight, Section.__name__
            )

        section_object = await manage_section_state(
            section_object,
            new_max_weight,
        )

    if new_max_racks := section_data.get("max_racks"):
        if new_max_racks < section_object.occupied_racks:
            raise TooLittleRacksAmountException(
                new_max_racks, section_object.occupied_racks
            )
        section_object = await manage_section_state(section_object, new_max_racks)

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
    if not (section_object := await if_exists(Section, "id", section_id, session)):
        raise DoesNotExist(Section.__name__, "id", section_id)

    if section_object.racks:
        raise SectionIsNotEmptyException(resource="racks")

    if section_object.occupied_weight or section_object.reserved_weight:
        raise SectionIsNotEmptyException(resource="occupied or reserved weight")

    statement = delete(Section).filter(Section.id == section_id)
    result = await session.execute(statement)
    warehouse = await if_exists(Warehouse, "id", section_object.warehouse_id, session)

    warehouse = await manage_warehouse_state(warehouse, sections_involved=True)
    session.add(warehouse)

    await session.commit()
    return result
