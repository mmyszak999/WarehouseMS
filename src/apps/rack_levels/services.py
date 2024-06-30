from decimal import Decimal
from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_levels.models import RackLevel
from src.apps.rack_levels.schemas import (
    RackLevelBaseOutputSchema,
    RackLevelInputSchema,
    RackLevelOutputSchema,
    RackLevelUpdateSchema,
)
from src.apps.racks.models import Rack
from src.apps.racks.schemas import (
    RackBaseOutputSchema,
    RackInputSchema,
    RackOutputSchema,
    RackUpdateSchema,
)
from src.apps.racks.services import manage_rack_state
from src.apps.sections.models import Section
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    NotEnoughRackResourcesException,
    RackLevelIsNotEmptyException,
    ServiceException,
    TooLittleRackLevelSlotsAmountException,
    TooLittleWeightAmountException,
    WeightLimitExceededException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_rack_level(
    session: AsyncSession, rack_level_input: RackLevelInputSchema
) -> RackOutputSchema:
    rack_level_data = rack_level_input.dict()
    rack_id = rack_level_data.get("rack_id")
    if not (rack_object := await if_exists(Rack, "id", rack_id, session)):
        raise DoesNotExist(Rack.__name__, "id", rack_id)

    if not rack_object.available_racks:
        raise NotEnoughRackResourcesException(
            resource="rack levels", reason="no more available rack levels to use"
        )

    if (
        rack_level_max_weight := rack_level_data.get("max_weight")
    ) > rack_object.weight_to_reserve:
        raise NotEnoughRackResourcesException(
            reason="amount of available rack weight to reserve exceeded",
            resource="rack levels",
        )

    # there probably will be created rack level slots (the same amount as max slots)
    new_rack_level = RackLevel(**rack_level_data)
    session.add(new_rack_level)
    rack = await manage_rack_state(
        rack_object,
        adding_resources_to_section=False,
        levels_involved=True,
        reserved_weight_involved=True,
        stock_weight=rack_level_max_weight,
    )
    session.add(rack)
    await session.commit()

    return RackLevelOutputSchema.from_orm(new_rack_level)


async def get_single_rack_level(
    session: AsyncSession,
    rack_level_id: str,
    output_schema: BaseModel = RackLevelOutputSchema,
) -> Union[RackLevelOutputSchema, RackLevelBaseOutputSchema]:
    if not (
        rack_level_object := await if_exists(RackLevel, "id", rack_level_id, session)
    ):
        raise DoesNotExist(RackLevel.__name__, "id", rack_level_id)

    return output_schema.from_orm(rack_level_object)


async def get_all_rack_levels(
    session: AsyncSession,
    page_params: PageParams,
    output_schema: BaseModel = RackLevelBaseOutputSchema,
) -> Union[
    PagedResponseSchema[RackLevelBaseOutputSchema],
    PagedResponseSchema[RackLevelOutputSchema],
]:
    query = select(RackLevel)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=RackLevel,
        page_params=page_params,
        session=session,
    )


async def manage_rack_level_state(
    rack_level_object: Rack = None,
    max_weight: Decimal = None,
    max_slots: int = None,
    adding_resources_to_rack_level: bool = True,
    weight_involved: bool = None,
    slots_involved: bool = None,
    stock_weight: Decimal = None,
) -> Rack:
    if not (isinstance(rack_level_object, RackLevel)):
        raise ServiceException("Rack level object was not provided! ")

    multiplier = -1 if adding_resources_to_rack_level else 1

    if weight_involved:
        if stock_weight is None:
            raise ServiceException("Stock weight was not provided! ")
        rack_level_object.available_weight -= multiplier * stock_weight
        rack_level_object.occupied_weight += multiplier * stock_weight

    if slots_involved:
        rack_level_object.available_slots -= multiplier
        rack_level_object.occupied_slots += multiplier

    if max_weight is not None:
        new_available_weight = max_weight - rack_level_object.occupied_weight
        rack_level_object.available_weight = new_available_weight

    if max_slots is not None:
        new_available_slots = max_slots - rack_level_object.occupied_slots
        rack_level_object.available_slots = new_available_slots

    return rack_level_object


async def update_single_rack_level(
    session: AsyncSession, rack_level_input: RackLevelUpdateSchema, rack_level_id: str
) -> RackOutputSchema:
    if not (
        rack_level_object := await if_exists(RackLevel, "id", rack_level_id, session)
    ):
        raise DoesNotExist(RackLevel.__name__, "id", rack_level_id)

    if not (
        rack_object := await if_exists(Rack, "id", rack_level_object.rack_id, session)
    ):
        raise DoesNotExist(Rack.__name__, "id", rack_object.rack_id)

    rack_level_data = rack_level_input.dict(exclude_unset=True, exclude_none=True)

    if new_max_weight := rack_level_data.get("max_weight"):
        if new_max_weight < rack_level_object.occupied_weight:
            raise TooLittleWeightAmountException(
                new_max_weight, rack_level_object.occupied_weight, RackLevel.__name__
            )

        max_weight_difference = new_max_weight - rack_level_object.max_weight
        rack_object = await manage_rack_state(
            rack_level_object.rack,
            max_weight=rack_level_object.max_weight,
            stock_weight=max_weight_difference,
        )
        session.add(rack_object)

    if new_max_slots := rack_level_data.get("max_slots"):
        if new_max_slots < rack_level_object.occupied_slots:
            raise TooLittleRackLevelSlotsAmountException(
                new_max_slots, rack_level_object.occupied_slots
            )

    rack_level_object = await manage_rack_level_state(
        rack_level_object, new_max_weight, new_max_levels
    )
    session.add(rack_level_object)

    if rack_level_data:
        statement = (
            update(RackLevel)
            .filter(RackLevel.id == rack_level_id)
            .values(**rack_level_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(rack_level_object)

    return await get_single_rack_level(session, rack_level_id=rack_level_id)


async def delete_single_rack_level(session: AsyncSession, rack_level_id: str):
    if not (
        rack_level_object := await if_exists(RackLevel, "id", rack_level_id, session)
    ):
        raise DoesNotExist(RackLevel.__name__, "id", rack_level_id)

    if rack_level_object.occupied_weight:
        raise RackLevelIsNotEmptyException(resource="occupied weight")

    if rack_level_object.occupied_slots:
        raise RackLevelIsNotEmptyException(resource="occupied slots")

    statement = delete(Rack).filter(Rack.id == rack_id)

    if not (rack := await if_exists(Rack, "id", rack_level_object.rack_id, session)):
        raise DoesNotExist(Rack.__name__, "id", rack_level_object.rack_id)

    rack = await manage_rack_state(
        rack,
        slots_involved=True,
        reserved_weight_involved=True,
        stock_weight=rack_level_object.max_weight,
    )
    session.add(rack)
    result = await session.execute(statement)

    await session.commit()
    return result
