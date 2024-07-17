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
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas.stock_schemas import StockRackLevelSlotInputSchema
from src.core.exceptions import (
    AlreadyExists,
    CannotMoveIssuedStockException,
    CantActivateRackLevelSlotException,
    CantDeactivateRackLevelSlotException,
    DoesNotExist,
    ExistingGapBetweenInactiveSlotsToDeleteException,
    IsOccupied,
    NoAvailableSlotsInRackLevelException,
    NoAvailableWeightInRackLevelException,
    NotEnoughRackLevelResourcesException,
    RackLevelSlotIsNotEmptyException,
    ServiceException,
    StockAlreadyInRackLevelException,
    TooSmallInactiveSlotsQuantityException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_rack_level_slot(
    session: AsyncSession,
    rack_level_slot_input: RackLevelSlotInputSchema,
    creating_rack_level: bool,
) -> None:
    rack_level_slot_data = rack_level_slot_input.dict()
    rack_level_id = rack_level_slot_data.get("rack_level_id")
    if not (
        rack_level_object := await if_exists(RackLevel, "id", rack_level_id, session)
    ):
        raise DoesNotExist(RackLevel.__name__, "id", rack_level_id)

    if (not rack_level_object.available_slots) and creating_rack_level:
        raise NotEnoughRackLevelResourcesException(
            resource="slots", reason="no more available rack level slots to use"
        )

    if (
        (rack_level_slot_number := rack_level_slot_data.get("rack_level_slot_number"))
        > rack_level_object.max_slots
    ) and creating_rack_level:
        raise NotEnoughRackLevelResourcesException(
            reason="max rack level slot number exceeded - pick number from the available slots",
            resource="slots",
        )

    rack_level_slot_with_the_same_rack_level_and_number_check = select(
        RackLevelSlot
    ).filter(
        RackLevelSlot.rack_level_id == rack_level_id,
        RackLevelSlot.rack_level_slot_number == rack_level_slot_number,
    )

    if existing_rack_level_slot := (
        await session.scalar(rack_level_slot_with_the_same_rack_level_and_number_check)
    ):
        raise AlreadyExists(
            RackLevelSlot.__name__,
            "rack_level_slot_number",
            existing_rack_level_slot.rack_level_slot_number,
            comment=("(in the requested rack level)"),
        )

    new_rack_level_slot = RackLevelSlot(**rack_level_slot_data)
    session.add(new_rack_level_slot)
    session.add(rack_level_object)
    await session.flush()

    return new_rack_level_slot


async def get_single_rack_level_slot(
    session: AsyncSession,
    rack_level_slot_id: str,
    output_schema: BaseModel = RackLevelSlotOutputSchema,
) -> Union[RackLevelSlotOutputSchema, RackLevelSlotBaseOutputSchema]:
    if not (
        rack_level_slot_object := await if_exists(
            RackLevelSlot, "id", rack_level_slot_id, session
        )
    ):
        raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)
    print(rack_level_slot_object.__dict__)

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
    session: AsyncSession,
    rack_level_slot_input: RackLevelSlotUpdateSchema,
    rack_level_slot_id: str,
) -> RackLevelSlotOutputSchema:
    if not (
        rack_level_slot_object := await if_exists(
            RackLevelSlot, "id", rack_level_slot_id, session
        )
    ):
        raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)

    rack_level_slot_data = rack_level_slot_input.dict(
        exclude_unset=True, exclude_none=True
    )

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
    session: AsyncSession, rack_level_slot_id: str, activate_slot: bool = True
) -> dict[str, str]:
    from src.apps.rack_levels.services import manage_rack_level_state

    if not (
        rack_level_slot_object := await if_exists(
            RackLevelSlot, "id", rack_level_slot_id, session
        )
    ):
        raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)

    if rack_level_slot_object.stock:
        raise RackLevelSlotIsNotEmptyException(resource="Slot contains a stock! ")

    if rack_level_slot_object.is_active and activate_slot:
        raise CantActivateRackLevelSlotException(reason="Slot already activated! ")

    if not (rack_level_slot_object.is_active) and not (activate_slot):
        raise CantDeactivateRackLevelSlotException(reason="Slot already deactivated! ")

    if not (
        rack_level_object := await if_exists(
            RackLevel, "id", rack_level_slot_object.rack_level_id, session
        )
    ):
        raise DoesNotExist(
            RackLevel.__name__, "id", rack_level_slot_object.rack_level_id
        )

    rack_level_slot_object.is_active = activate_slot
    session.add(rack_level_slot_object)

    rack_level_object = await manage_rack_level_state(
        rack_level_object,
        manage_active_slots=True,
        adding_resources_to_rack_level=activate_slot,
    )
    session.add(rack_level_object)

    await session.commit()
    slot_action = "activated" if activate_slot else "deactivated"
    return {
        "message": f"The requested rack level slot was {slot_action} successfully! "
    }


async def deactivate_single_rack_level_slot(
    session: AsyncSession, rack_level_slot_id: str
) -> dict[str, str]:
    return await manage_single_rack_level_slot_state(
        session, rack_level_slot_id, activate_slot=False
    )


async def activate_single_rack_level_slot(
    session: AsyncSession, rack_level_slot_id: str
) -> dict[str, str]:
    return await manage_single_rack_level_slot_state(
        session, rack_level_slot_id, activate_slot=True
    )


async def manage_rack_level_slots_when_changing_rack_level_max_slots(
    session: AsyncSession,
    rack_level: RackLevel,
    max_slots_difference: int,
    creating_slots: bool,
) -> None:
    if max_slots_difference == 0:
        return

    rack_level_slots = rack_level.rack_level_slots
    rack_level_slot_numbers = [slot.rack_level_slot_number for slot in rack_level_slots]
    rack_level_slot_numbers.sort(reverse=True)

    max_slot_number = max(rack_level_slot_numbers)

    if creating_slots:
        for slot_number in range(
            max_slot_number + 1, (max_slot_number + max_slots_difference + 1)
        ):
            input_schema = RackLevelSlotInputSchema(
                rack_level_slot_number=slot_number,
                description=f"slot #{slot_number}",
                rack_level_id=rack_level.id,
            )
            await create_rack_level_slot(
                session, rack_level_slot_input=input_schema, creating_rack_level=False
            )
        return

    else:
        max_slots_difference *= -1
        slots_ids = [slot.id for slot in rack_level_slots]
        inactive_slots = await session.scalars(
            select(RackLevelSlot)
            .where(RackLevelSlot.is_active == False, RackLevelSlot.id.in_(slots_ids))
            .order_by(RackLevelSlot.rack_level_slot_number.desc())
            .limit(max_slots_difference)
        )
        inactive_slots = inactive_slots.unique().all()
        if len(inactive_slots) < max_slots_difference:
            raise TooSmallInactiveSlotsQuantityException(
                inactive_slots=len(inactive_slots)
            )

        if rack_level_slot_numbers[:max_slots_difference] != [
            slot.rack_level_slot_number for slot in inactive_slots
        ]:
            raise ExistingGapBetweenInactiveSlotsToDeleteException(
                slots_amount=max_slots_difference
            )

        rack_level.inactive_slots -= max_slots_difference
        session.add(rack_level)
        for slot in inactive_slots:
            await session.execute(
                delete(RackLevelSlot).filter(RackLevelSlot.id == slot.id)
            )
        return


async def manage_old_rack_level_slot_state(
    session: AsyncSession,
    stock_object: Stock,
    old_rack_level_slot_object: RackLevelSlot,
    old_rack_level_slot_id: str,
) -> RackLevel:
    from src.apps.stocks.services.stock_services import (
        manage_resources_state_when_managing_stocks,
    )

    old_rack_level_slot_object = await manage_resources_state_when_managing_stocks(
        session,
        old_rack_level_slot_object,
        adding_resources=True,
        stock_weight=stock_object.weight,
    )

    old_rack_level_slot_id = old_rack_level_slot_object.id
    stock_object.rack_level_slot_id = None
    return old_rack_level_slot_object


async def add_single_stock_to_rack_level_slot(
    session: AsyncSession,
    rack_level_slot_id: str,
    stock_schema: StockRackLevelSlotInputSchema,
    user_id: str,
) -> dict[str, str]:
    from src.apps.stocks.services.stock_services import (
        manage_resources_state_when_managing_stocks,
    )
    from src.apps.stocks.services.user_stock_services import create_user_stock_object
    from src.apps.waiting_rooms.services import manage_old_waiting_room_state

    if not (
        rack_level_slot_object := await if_exists(
            RackLevelSlot, "id", rack_level_slot_id, session
        )
    ):
        raise DoesNotExist(RackLevelSlot.__name__, "id", rack_level_slot_id)

    stock_id = stock_schema.id
    if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
        raise DoesNotExist(Stock.__name__, "id", stock_id)

    if stock_object.is_issued:
        raise CannotMoveIssuedStockException

    if not rack_level_slot_object.rack_level.available_slots:
        raise NoAvailableSlotsInRackLevelException

    if rack_level_slot_object.rack_level.available_weight < stock_object.weight:
        raise NoAvailableWeightInRackLevelException

    _old_waiting_room_id = None
    _old_rack_level_slot_id = None
    _new_rack_level_slot_object = None

    if old_waiting_room_object := stock_object.waiting_room:
        old_waiting_room_object = await manage_old_waiting_room_state(
            session,
            stock_object,
            old_waiting_room_object,
            old_waiting_room_id=_old_waiting_room_id,
        )
        _old_waiting_room_id = old_waiting_room_object.id

    if old_rack_level_slot_object := stock_object.rack_level_slot:
        old_rack_level_slot_object = await manage_old_rack_level_slot_state(
            session,
            stock_object,
            old_rack_level_slot_object,
            old_rack_level_slot_id=_old_rack_level_slot_id,
        )
        _old_rack_level_slot_id = old_rack_level_slot_object.id

    _new_rack_level_slot_object = rack_level_slot_object
    await create_user_stock_object(
        session,
        stock_object.id,
        user_id,
        from_waiting_room_id=_old_waiting_room_id,
        to_rack_level_slot_id=_new_rack_level_slot_object.id,
        from_rack_level_slot_id=_old_rack_level_slot_id,
    )

    rack_level_slot = await manage_resources_state_when_managing_stocks(
        session,
        _new_rack_level_slot_object,
        stock_object.weight,
        adding_resources=False,
    )
    session.add(rack_level_slot)

    stock_object.rack_level_slot_id = rack_level_slot.id
    session.add(stock_object)
    await session.commit()

    return {"message": "Stock was successfully added to the rack level slot! "}
