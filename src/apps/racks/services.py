from decimal import Decimal
from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.racks.models import Rack
from src.apps.racks.schemas import (
    RackBaseOutputSchema,
    RackInputSchema,
    RackOutputSchema,
    RackUpdateSchema,
)
from src.apps.sections.models import Section
from src.apps.sections.services import manage_section_state
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    NotEnoughSectionResourcesException,
    NotEnoughWarehouseResourcesException,
    RackIsNotEmptyException,
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
from src.core.utils.orm import if_exists


async def create_rack(
    session: AsyncSession, rack_input: RackInputSchema
) -> RackOutputSchema:
    rack_data = rack_input.dict()
    section_id = rack_data.get("section_id")
    if not (section_object := await if_exists(Section, "id", section_id, session)):
        raise DoesNotExist(Section.__name__, "id", section_id)

    if not section_object.available_racks:
        raise NotEnoughSectionResourcesException(
            resource="racks", reason="no more available racks to use"
        )

    if (
        rack_max_weight := rack_data.get("max_weight")
    ) > section_object.weight_to_reserve:
        raise NotEnoughSectionResourcesException(
            reason="available section weight to reserve exceeded", resource="racks"
        )

    new_rack = Rack(**rack_data)
    session.add(new_rack)
    section = await manage_section_state(
        section_object,
        adding_resources_to_section=False,
        racks_involved=True,
        reserved_weight_involved=True,
        stock_weight=rack_max_weight,
    )
    session.add(section)

    await session.commit()
    return RackOutputSchema.from_orm(new_rack)


async def get_single_rack(
    session: AsyncSession,
    rack_id: str,
    output_schema: BaseModel = RackOutputSchema,
) -> Union[RackOutputSchema, RackBaseOutputSchema]:
    if not (rack_object := await if_exists(Rack, "id", rack_id, session)):
        raise DoesNotExist(Rack.__name__, "id", rack_id)

    return output_schema.from_orm(rack_object)


async def get_all_racks(
    session: AsyncSession,
    page_params: PageParams,
    output_schema: BaseModel = RackBaseOutputSchema,
) -> Union[
    PagedResponseSchema[RackBaseOutputSchema],
    PagedResponseSchema[RackOutputSchema],
]:
    query = select(Rack)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=Rack,
        page_params=page_params,
        session=session,
    )


async def manage_rack_state(
    rack_object: Rack = None,
    max_weight: Decimal = None,
    max_levels: int = None,
    adding_resources_to_rack: bool = True,
    levels_involved: bool = None,
    weight_involved: bool = None,
    stock_weight: Decimal = None,
) -> Rack:
    if not (isinstance(rack_object, Rack)):
        raise ServiceException("Rack object was not provided! ")

    multiplier = -1 if adding_resources_to_rack else 1

    if weight_involved:
        if stock_weight is None:
            raise ServiceException("Stock weight was not provided! ")
        rack_object.available_weight -= multiplier * stock_weight
        rack_object.occupied_weight += multiplier * stock_weight

    if reserved_weight_involved:
        if stock_weight is None:
            raise ServiceException("Stock weight was not provided! ")
        rack_object.weight_to_reserve -= multiplier * stock_weight
        rack_object.reserved_weight += multiplier * stock_weight

    if levels_involved:
        rack_object.available_levels -= multiplier
        rack_object.occupied_levels += multiplier

    if max_weight is not None:
        new_available_weight = max_weight - rack_object.occupied_weight
        rack_object.available_weight = new_available_weight

        if stock_weight is not None:
            rack_object.weight_to_reserve += stock_weight * multiplier
            rack_object.reserved_weight -= stock_weight * multiplier
        else:
            new_weight_to_reserve = max_weight - rack_object.reserved_weight
            rack_object.weight_to_reserve = new_weight_to_reserve

    if max_levels is not None:
        new_available_levels = max_levels - rack_object.occupied_levels
        rack_object.available_levels = new_available_levels

    return rack_object


async def update_single_rack(
    session: AsyncSession, rack_input: RackUpdateSchema, rack_id: str
) -> RackOutputSchema:
    if not (rack_object := await if_exists(Rack, "id", rack_id, session)):
        raise DoesNotExist(Rack.__name__, "id", rack_id)

    if not (
        section_object := await if_exists(
            Section, "id", rack_object.section_id, session
        )
    ):
        raise DoesNotExist(Section.__name__, "id", rack_object.section_id)

    rack_data = rack_input.dict(exclude_unset=True, exclude_none=True)

    if new_max_weight := rack_data.get("max_weight"):
        if new_max_weight < rack_object.occupied_weight:
            raise TooLittleWeightAmountException(
                new_max_weight, rack_object.occupied_weight, Rack.__name__
            )

        if new_max_weight > (section_object.weight_to_reserve + rack_object.max_weight):
            raise WeightLimitExceededException(
                new_max_weight,
                (section_object.weight_to_reserve + rack_object.max_weight),
            )

        max_weight_difference = new_max_weight - rack_object.max_weight
        section_object = await manage_section_state(
            rack_object.section,
            max_weight=section_object.max_weight,
            stock_weight=max_weight_difference,
        )
        session.add(section_object)

    if new_max_levels := rack_data.get("max_levels"):
        if new_max_levels < rack_object.occupied_levels:
            raise TooLittleRackLevelsAmountException(
                new_max_levels, rack_object.occupied_levels
            )

    rack_object = await manage_rack_state(rack_object, new_max_weight, new_max_levels)
    session.add(rack_object)

    if rack_data:
        statement = update(Rack).filter(Rack.id == rack_id).values(**rack_data)

        await session.execute(statement)
        await session.commit()
        await session.refresh(rack_object)

    return await get_single_rack(session, rack_id=rack_id)


async def delete_single_rack(session: AsyncSession, rack_id: str):
    if not (rack_object := await if_exists(Rack, "id", rack_id, session)):
        raise DoesNotExist(Rack.__name__, "id", rack_id)

    if rack_object.rack_levels:
        raise RackIsNotEmptyException(resource="rack levels")

    if rack_object.occupied_weight:
        raise RackIsNotEmptyException(resource="occupied weight")

    statement = delete(Rack).filter(Rack.id == rack_id)

    section = await if_exists(Section, "id", rack_object.section_id, session)

    section = await manage_section_state(
        section,
        racks_involved=True,
        reserved_weight_involved=True,
        stock_weight=rack_object.max_weight,
    )
    session.add(section)
    result = await session.execute(statement)

    await session.commit()
    return result
