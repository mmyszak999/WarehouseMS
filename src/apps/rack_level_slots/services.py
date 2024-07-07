from decimal import Decimal
from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.rack_level_slots.models import RackLevelSlot
from src.apps.rack_level_slots.schemas import (
    RackLevelSlotBaseOutputSchema,
    RackLevelSlotInputSchema,
    RackLevelSlotOutputSchema,
    RackLevelSlotUpdateSchema,
)
from src.apps.rack_levels.models import RackLevel
from src.apps.rack_levels.schemas import (
    RackLevelBaseOutputSchema,
    RackLevelInputSchema,
    RackLevelOutputSchema,
    RackLevelUpdateSchema,
)
from src.apps.rack_levels.services import manage_rack_level_state
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    NotEnoughRackLevelResourcesException,
    ServiceException,
    RackLevelSlotIsNotEmptyException,
    CantActivateRackLevelSlotException,
    CantDeactivateRackLevelSlotException
    )
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_rack_level_slot(
    session: AsyncSession, rack_level_slot_input: RackLevelSlotInputSchema
) -> None:
    rack_level_slot_data = rack_level_slot_input.dict()
    rack_level_id = rack_level_slot_data.get("rack_level_id")
    if not (rack_level_object := await if_exists(RackLevel, "id", rack_level_id, session)):
        raise DoesNotExist(RackLevel.__name__, "id", rack_level_id)

    if not rack_level_object.available_slots:
        raise NotEnoughRackLevelResourcesException(
            resource="slots", reason="no more available rack level slots to use"
        )

    if (
        rack_level_slot_number := rack_level_slot_data.get("rack_level_slot_number")
    ) > rack_level_object.max_slots:
        raise NotEnoughRackLevelResourcesException(
            reason="max rack level slot number exceeded - pick number from the available slots",
            resource="slots",
        )

    rack_level_slot_with_the_same_rack_level_and_number_check = select(RackLevelSlot).filter(
        RackLevelSlot.rack_level_id == rack_level_id, RackLevelSlot.rack_level_slot_number == rack_level_slot_number
    )

    if existing_rack_level_slot := (
        await session.scalar(rack_level_slot_with_the_same_level_and_rack_check)
    ):
        raise AlreadyExists(
            RackLevelSlot.__name__,
            "rack_level_slot_number",
            existing_rack_level_slot.rack_level_slot_number,
            comment=("(in the requested rack level)"),
        )

    new_rack_level_slot = RackLevelSlot(**rack_level_slot_data)
    session.add(new_rack_level_slot)
    rack_level = await manage_rack_level_state(
        rack_level_object,
        adding_resources_to_rack_level=False,
        slots_involved=True
    )
    session.add(rack_level)
    await session.commit()
    await session.refresh(rack_level)

    return

async def get_single_rack_level_slot(
    session: AsyncSession,
    rack_level_slot_id: str,
    output_schema: BaseModel = RackLevelSlotOutputSchema,
) -> Union[RackLevelSlotOutputSchema, RackLevelSlotBaseOutputSchema]:
    if not (
        rack_level_slot_object := await if_exists(RackLevelSlot, "id", rack_level_slot_id, session)
    ):
        raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)

    return output_schema.from_orm(rack_level_slot_object)


async def get_all_rack_level_slots(
    session: AsyncSession,
    page_params: PageParams,
    output_schema: BaseModel = RackLevelSlotBaseOutputSchema,
) -> Union[
    PagedResponseSchema[RackLevelSlotBaseOutputSchema],
    PagedResponseSchema[RackLevelSlotOutputSchema],
]:
    query = select(RackLevelSlot)

    return await paginate(
        query=query,
        response_schema=output_schema,
        table=RackLevelSlot,
        page_params=page_params,
        session=session,
    )


async def update_single_rack_level_slot(
    session: AsyncSession, rack_level_slot_input: RackLevelSlotUpdateSchema, rack_level_slot_id: str
) -> RackLevelSlotOutputSchema:
    if not (
        rack_level_slot_object := await if_exists(RackLevelSlot, "id", rack_level_slot_id, session)
    ):
        raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)
    
    rack_level_slot_data = rack_level_input.dict(exclude_unset=True, exclude_none=True)
    
    if rack_level_slot_data:
        statement = (
            update(RackLevelSlot)
            .filter(RackLevelSlot.id == rack_level_slot_id)
            .values(**rack_level_slot_data)
        )

        await session.execute(statement)
        await session.commit()
        await session.refresh(rack_level_slot_object)

    return await get_single_rack_level_slot(
        session, rack_level_slot_id=rack_level_slot_id
    )


async def manage_single_rack_level_slot_state(
    session: AsyncSession, rack_level_slot_id: str, activate_slot: bool=True
) -> dict[str, str]:
    if not (
        rack_level_slot_object := await if_exists(
            RackLevelSlot, "id", rack_level_slot_id, session
        )
    ):
        raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)

    if rack_level_slot_object.stock:
        pass
        #raise RackLevelSlotIsNotEmptyException(resource="occupied slot")

    if not (rack_level_object := await if_exists(
        RackLevel, "id", rack_level_slot_object.rack_level_id, session)
    ):
        raise DoesNotExist(RackLevel.__name__, "id", rack_level_slot_object.rack_level_id)
    
    if (not rack_level_object.available_slots) and (not activate_slot):
        raise CantDeactivateRackLevelSlotException(
            reason="all available slots are occupied! "
        )
    
    if (rack_level_object.active_slots == rack_level_object.max_slots) and activate_slot:
        raise CantActivateRackLevelSlotException(
            reason="reached max amount of activate slots in the rack level! "
        )

    rack_level_object = await manage_rack_level_state(
        rack_level_object,
        manage_active_slots=True,
        adding_resources_to_rack_level=activate_slot
    )
    
    session.add(rack_level_slot_object)
    session.add(rack_level_object)

    await session.commit()
    slot_action = "activated" if activate_slot else "deactivated"
    return {"message": f"The requested rack level slot was {slot_action} successfully! "}