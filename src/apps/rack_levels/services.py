from decimal import Decimal
from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.stocks.schemas.stock_schemas import StockRackLevelInputSchema
from src.apps.stocks.models import Stock
from src.apps.waiting_rooms.services import manage_old_waiting_room_state
from src.apps.rack_level_slots.services import manage_old_rack_level_slot_state
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
from src.apps.rack_level_slots.models import RackLevelSlot
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    NotEnoughRackLevelResourcesException,
    NotEnoughRackResourcesException,
    NotEnoughSectionResourcesException,
    RackLevelIsNotEmptyException,
    ServiceException,
    TooLittleRackLevelSlotsAmountException,
    TooLittleWeightAmountException,
    WeightLimitExceededException,
    NoAvailableRackLevelSlotException,
    StockAlreadyInRackLevelException,
    NoAvailableSlotsInRackLevelException,
    NoAvailableWeightInRackLevelException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists


async def create_rack_level(
    session: AsyncSession, rack_level_input: RackLevelInputSchema
) -> RackLevelBaseOutputSchema:
    from src.apps.rack_level_slots.schemas import RackLevelSlotInputSchema
    from src.apps.rack_level_slots.services import create_rack_level_slot

    rack_level_data = rack_level_input.dict()
    rack_id = rack_level_data.get("rack_id")
    if not (rack_object := await if_exists(Rack, "id", rack_id, session)):
        raise DoesNotExist(Rack.__name__, "id", rack_id)

    if not rack_object.available_levels:
        raise NotEnoughRackResourcesException(
            resource="levels", reason="no more available rack levels to use"
        )

    if (
        rack_level_max_weight := rack_level_data.get("max_weight")
    ) > rack_object.weight_to_reserve:
        raise NotEnoughRackResourcesException(
            reason="amount of available rack weight to reserve exceeded",
            resource="rack weight",
        )

    if (
        rack_level_number := rack_level_data.get("rack_level_number")
    ) > rack_object.max_levels:
        raise NotEnoughRackResourcesException(
            reason="max rack level number exceeded - pick number from the available levels",
            resource="rack levels",
        )

    rack_level_with_the_same_level_and_rack_check = select(RackLevel).filter(
        RackLevel.rack_id == rack_id, RackLevel.rack_level_number == rack_level_number
    )

    if existing_rack_level := (
        await session.scalar(rack_level_with_the_same_level_and_rack_check)
    ):
        raise AlreadyExists(
            RackLevel.__name__,
            "rack_level_number",
            existing_rack_level.rack_level_number,
            comment=("(in the requested rack)"),
        )

    new_rack_level = RackLevel(**rack_level_data)
    session.add(new_rack_level)
    rack = await manage_rack_state(
        rack_object,
        adding_resources_to_rack=False,
        levels_involved=True,
        reserved_weight_involved=True,
        stock_weight=rack_level_max_weight,
    )
    session.add(rack)
    await session.flush()

    for slot_number in range(1, rack_level_data.get("max_slots") + 1):
        input_schema = RackLevelSlotInputSchema(
            rack_level_slot_number=slot_number,
            description=f"slot #{slot_number}",
            rack_level_id=new_rack_level.id,
        )
        await create_rack_level_slot(
            session, rack_level_slot_input=input_schema, creating_rack_level=True
        )

    await session.commit()
    await session.refresh(rack)
    await session.refresh(new_rack_level)

    return RackLevelBaseOutputSchema.from_orm(new_rack_level)


async def get_single_rack_level(
    session: AsyncSession,
    rack_level_id: str,
    output_schema: BaseModel = RackLevelOutputSchema,
) -> Union[RackLevelBaseOutputSchema, RackLevelOutputSchema]:
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
    rack_level_object: RackLevel = None,
    max_weight: Decimal = None,
    max_slots: int = None,
    adding_resources_to_rack_level: bool = True,
    weight_involved: bool = None,
    slots_involved: bool = None,
    stock_weight: Decimal = None,
    manage_active_slots: bool = None,
) -> RackLevel:
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

    if manage_active_slots:
        rack_level_object.active_slots -= multiplier
        rack_level_object.inactive_slots += multiplier
        rack_level_object.available_slots -= multiplier

    if max_weight is not None:
        new_available_weight = max_weight - rack_level_object.occupied_weight
        rack_level_object.available_weight = new_available_weight

    if max_slots is not None:
        new_available_slots = (
            max_slots
            - rack_level_object.occupied_slots
            - rack_level_object.inactive_slots
        )
        rack_level_object.available_slots = new_available_slots
        rack_level_object.active_slots = (
            new_available_slots + rack_level_object.occupied_slots
        )
    return rack_level_object


async def update_single_rack_level(
    session: AsyncSession, rack_level_input: RackLevelUpdateSchema, rack_level_id: str
) -> RackLevelOutputSchema:
    from src.apps.rack_level_slots.services import (
        manage_rack_level_slots_when_changing_rack_level_max_slots,
    )

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

        if new_max_weight > (
            rack_object.weight_to_reserve + rack_level_object.max_weight
        ):
            raise WeightLimitExceededException(
                new_max_weight,
                (rack_object.weight_to_reserve + rack_level_object.max_weight),
            )

        max_weight_difference = new_max_weight - rack_level_object.max_weight
        rack_object = await manage_rack_state(
            rack_level_object.rack,
            max_weight=rack_object.max_weight,
            stock_weight=max_weight_difference,
        )
        session.add(rack_object)

    if new_max_slots := rack_level_data.get("max_slots"):
        if new_max_slots < rack_level_object.occupied_slots:
            raise TooLittleRackLevelSlotsAmountException(
                new_max_slots, rack_level_object.occupied_slots
            )

        max_slots_difference = new_max_slots - rack_level_object.max_slots
        if (new_max_slots < rack_level_object.max_slots) and (
            (rack_level_object.available_slots - max_slots_difference) < 0
        ):
            raise NotEnoughRackLevelResourcesException(
                resource="slots",
                reason="new max slots amount too small in relation to the available slots amount",
            )

        creating_slots = False if max_slots_difference <= 0 else True
        await manage_rack_level_slots_when_changing_rack_level_max_slots(
            session,
            rack_level_object,
            max_slots_difference,
            creating_slots=creating_slots,
        )

    rack_level_object = await manage_rack_level_state(
        rack_level_object, new_max_weight, new_max_slots
    )
    await session.flush()

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

    """if rack_level_object.occupied_weight:
        raise RackLevelIsNotEmptyException(resource="occupied weight")"""

    """if rack_level_object.occupied_slots:
        raise RackLevelIsNotEmptyException(resource="occupied slots")"""

    statement = delete(RackLevel).filter(RackLevel.id == rack_level_id)

    if not (rack := await if_exists(Rack, "id", rack_level_object.rack_id, session)):
        raise DoesNotExist(Rack.__name__, "id", rack_level_object.rack_id)

    rack = await manage_rack_state(
        rack,
        levels_involved=True,
        reserved_weight_involved=True,
        stock_weight=rack_level_object.max_weight,
    )
    session.add(rack)
    result = await session.execute(statement)

    await session.commit()
    return result

async def add_single_stock_to_rack_level(
    session: AsyncSession,
    rack_level_id: str,
    stock_schema: StockRackLevelInputSchema,
    user_id: str,
) -> dict[str, str]:
    from src.apps.stocks.services.user_stock_services import create_user_stock_object
    from src.apps.stocks.services.stock_services import manage_resources_state_when_managing_stocks

    if not (
        rack_level_object := await if_exists(
            RackLevel, "id", rack_level_id, session
        )
    ):
        raise DoesNotExist(RackLevel.__name__, "id", rack_level_id)

    stock_id = stock_schema.id
    if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
        raise DoesNotExist(Stock.__name__, "id", stock_id)

    if stock_object.is_issued:
        raise CannotMoveIssuedStockException

    if stock_object.rack_level_slot:
        if stock_object.rack_level_slot.rack_level_id == rack_level_slot_id:
            raise StockAlreadyInRackLevelException

    if not rack_level_slot_object.rack_level.available_slots:
        raise NoAvailableSlotsInRackLevelException

    if rack_level_slot_object.rack_level.available_weight < stock_object.weight:
        raise NoAvailableWeightInRackLevelException
    
    _old_waiting_room_id = None
    _old_rack_level_slot_id = None 
    _new_rack_level_slot_object = None
    
    statement = (
                select(RackLevelSlot)
                .filter(
                    RackLevelSlot.stock == None,
                    RackLevelSlot.is_active == True,
                    RackLevelSlot.rack_level_id == rack_level_id)
                .order_by(RackLevelSlot.rack_level_slot_number.asc())
                .limit(1)
            )

    available_rack_level_slot = await session.execute(statement)
    rack_level_slot_object = available_rack_level_slot.scalar()
    if not rack_level_slot_object:
        raise NoAvailableRackLevelSlotException(
            stock_object.product.name, stock_object.product_count, stock.weight
        )
    _new_rack_level_slot_object = rack_level_slot_object
    
    if old_waiting_room_object := stock_object.waiting_room:
        old_waiting_room_object = await manage_old_waiting_room_state(
            session,
            stock_object,
            old_waiting_room_object,
            old_waiting_room_id=_old_waiting_room_id
        )
        _old_waiting_room_id = old_waiting_room_object.id
        
    if old_rack_level_slot_object := stock_object.rack_level_slot:
        old_rack_level_slot_object = await manage_old_rack_level_slot_state(
            session,
            stock_object,
            old_rack_level_slot_object,
            old_rack_level_slot_id=_old_rack_level_slot_id
        )
        _old_rack_level_slot_id = old_rack_level_slot_object.id
        
    user_stock = await create_user_stock_object(
            session,
            stock_object.id,
            user_id,
            from_waiting_room_id=_old_waiting_room_id,
            to_rack_level_slot_id=_new_rack_level_slot_object.id,
            from_rack_level_slot_id=_old_rack_level_slot_id
        )
    
    rack_level_slot = await manage_resources_state_when_managing_stocks(
        session, _new_rack_level_slot_object, stock_object.weight, adding_resources=False
    )
    session.add(rack_level_slot)
    session.add(rack_level_object)
    
    stock_object.rack_level_slot_id = rack_level_slot.id
    session.add(stock_object)
    await session.commit()

    return {"message": "Stock was successfully added to the rack level! "}
