import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.services import create_issue
from src.apps.products.models import Product
from src.apps.sections.schemas import (
    SectionOutputSchema
)
from src.apps.rack_levels.services import (
    create_rack_level
)
from src.core.factory.rack_factory import (
    RackInputSchemaFactory
)
from src.core.factory.rack_level_factory import (
    RackLevelInputSchemaFactory
)
from src.apps.racks.schemas import RackInputSchema, RackOutputSchema, RackUpdateSchema
from src.apps.racks.services import create_rack, get_all_racks, get_single_rack
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas.stock_schemas import (
    StockIssueInputSchema,
    StockOutputSchema,
)
from src.apps.rack_level_slots.schemas import RackLevelSlotOutputSchema
from src.apps.rack_level_slots.models import RackLevelSlot
from src.apps.stocks.services.stock_services import (
    create_stocks,
    get_all_available_stocks,
    get_all_stocks,
    get_single_stock,
    issue_stocks,
)
from src.apps.users.schemas import UserOutputSchema
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.schemas import WaitingRoomOutputSchema
from src.apps.waiting_rooms.services import create_waiting_room
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    MissingProductDataException,
    NoAvailableWaitingRoomsException,
    AmbiguousStockStoragePlaceDuringReceptionException,
    ServiceException,
    NotEnoughRackLevelResourcesException,
    NoAvailableRackLevelSlotException
)
from src.core.factory.issue_factory import IssueInputSchemaFactory
from src.core.factory.stock_factory import StockInputSchemaFactory
from src.apps.rack_levels.models import RackLevel
from src.core.factory.waiting_room_factory import WaitingRoomInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import db_products
from tests.test_sections.conftest import db_sections
from tests.test_stocks.conftest import db_stocks
from tests.test_rack_level_slots.conftest import db_rack_level_slots
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from tests.test_warehouse.conftest import db_warehouse


@pytest.mark.asyncio
async def test_if_stocks_were_created_correctly(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    product_count = 5
    stock_inputs = [
        StockInputSchemaFactory().generate(
            product_weight=product.weight,
            product_count=product_count,
            product_id=product.id,
        )
        for product in db_products.results
    ]

    stocks = await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None, None, None],
        rack_level_ids=[None, None, None],
        rack_level_slots_ids=[None, None, None],
        testing=True,
        input_schemas=stock_inputs,
    )

    assert {product_count} == {stock.product_count for stock in stocks}
    assert {product.id for product in db_products.results} == {
        stock.product_id for stock in stocks
    }


@pytest.mark.asyncio
async def test_raise_exception_when_product_data_is_missing(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(MissingProductDataException):
        await create_stocks(
            async_session, user_id=db_staff_user.id, waiting_rooms_ids=[None],
            rack_level_ids=[None], rack_level_slots_ids=[None],
        )


@pytest.mark.asyncio
async def test_raise_exception_when_there_is_no_waiting_room_available_for_new_stocks(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]

    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=5, max_weight=1
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )
    await async_session.flush()

    with pytest.raises(NoAvailableWaitingRoomsException):
        await create_stocks(
            async_session,
            user_id=db_staff_user.id,
            products=products,
            product_counts=product_counts,
            waiting_rooms_ids=[None],
            rack_level_ids=[None],
            rack_level_slots_ids=[None],
        )


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_with_provided_id_does_not_exist_when_creating_stocks(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]
    with pytest.raises(DoesNotExist):
        await create_stocks(
            async_session,
            user_id=db_staff_user.id,
            products=products,
            product_counts=product_counts,
            waiting_rooms_ids=[generate_uuid()],
            rack_level_ids=[None],
            rack_level_slots_ids=[None],
        )


@pytest.mark.asyncio
async def test_check_if_stocks_are_created_correctly_with_provided_waiting_room_id(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):
    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]

    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=5, max_weight=9000
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )
    await async_session.flush()

    stocks = await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        products=products,
        product_counts=product_counts,
        waiting_rooms_ids=[waiting_room.id],
        rack_level_ids=[None],
        rack_level_slots_ids=[None],
    )

    assert stocks[0].waiting_room_id == waiting_room.id


@pytest.mark.asyncio
async def test_raise_exception_when_waiting_room_with_provided_id_is_not_available_for_new_stocks(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]

    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=5, max_weight=1
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )
    await async_session.flush()

    with pytest.raises(NoAvailableWaitingRoomsException):
        await create_stocks(
            async_session,
            user_id=db_staff_user.id,
            products=products,
            product_counts=product_counts,
            waiting_rooms_ids=[waiting_room.id],
            rack_level_ids=[None],
            rack_level_slots_ids=[None],
        )


@pytest.mark.asyncio
async def test_check_if_new_stock_will_be_correctly_added_to_available_waiting_room(
    async_session: AsyncSession,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=5, max_weight=9000
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )
    await async_session.flush()

    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]
    stocks = await create_stocks(
        async_session, db_staff_user.id, [waiting_room.id], 
        rack_level_ids=[None], rack_level_slots_ids=[None],
        products=products, product_counts=product_counts
    )
    await async_session.flush()

    assert stocks[0].waiting_room_id == waiting_room.id
    assert waiting_room.current_stock_weight == stocks[0].weight
    assert waiting_room.occupied_slots == 1


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_stock(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    with pytest.raises(DoesNotExist):
        await get_single_stock(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_getting_issued_stock(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    issued_stocks = [stock for stock in db_stocks.results if stock.is_issued]
    with pytest.raises(CannotRetrieveIssuedStockException):
        await get_single_stock(async_session, issued_stocks[0].id)


@pytest.mark.asyncio
async def test_if_all_available_stocks_were_returned(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    stocks = await get_all_available_stocks(async_session, PageParams(page=1, size=5))
    assert stocks.total == db_stocks.total - 1


@pytest.mark.asyncio
async def test_if_all_stocks_were_returned(
    async_session: AsyncSession, db_stocks: PagedResponseSchema[StockOutputSchema]
):
    stocks = await get_all_stocks(async_session, PageParams(page=1, size=5))
    assert stocks.total == db_stocks.total


@pytest.mark.asyncio
async def test_if_stocks_are_issued_correctly(
    async_session: AsyncSession,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_staff_user: UserOutputSchema,
):

    products = [
        await if_exists(Product, "id", db_products.results[0].id, async_session)
    ]
    product_counts = [4]

    waiting_room_input = WaitingRoomInputSchemaFactory().generate(
        max_stocks=5, max_weight=9000
    )
    waiting_room = await create_waiting_room(
        async_session, waiting_room_input, testing=True
    )
    await async_session.flush()

    stocks = await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        products=products,
        product_counts=product_counts,
        waiting_rooms_ids=[waiting_room.id],
        rack_level_ids=[None],
        rack_level_slots_ids=[None],
    )

    stock_object = stocks[0]
    waiting_room_before = await if_exists(
        WaitingRoom, "id", stock_object.waiting_room_id, async_session
    )

    
    issue_schema = IssueInputSchemaFactory().generate(
        stock_ids=[StockIssueInputSchema(id=stock_object.id)]
    )
    issue = await create_issue(async_session, issue_schema, db_staff_user.id)

    await async_session.refresh(stock_object)

    waiting_room_after = await if_exists(
        WaitingRoom, "id", waiting_room_before.id, async_session
    )

    assert {stock.id for stock in issue.stocks} == {stock_object.id}
    assert stock_object.waiting_room == None
    assert set(waiting_room_before.stocks) - set([stock_object]) == set(
        waiting_room_after.stocks
    )


@pytest.mark.asyncio
async def test_raise_exception_when_provided_multiple_stock_storage_places(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    with pytest.raises(AmbiguousStockStoragePlaceDuringReceptionException):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[generate_uuid()],
        rack_level_ids=[generate_uuid()],
        rack_level_slots_ids=[None],
        product_counts=[product_count],
        products=[product]
        )


@pytest.mark.asyncio
async def test_if_random_waiting_room_is_provided_for_stock_when_no_storage_place_was_assigned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    stocks = await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[None],
        rack_level_slots_ids=[None],
        product_counts=[product_count],
        products=[product]
        )

    stock = stocks[0]
    
    assert isinstance(stock.waiting_room, WaitingRoom) == True


@pytest.mark.asyncio
async def test_raise_exception_when_provided_nonexistent_rack_level_slot_id(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    with pytest.raises(DoesNotExist):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[None],
        rack_level_slots_ids=[generate_uuid()],
        product_counts=[product_count],
        products=[product]
        )

@pytest.mark.asyncio
async def test_raise_exception_when_rack_level_slot_is_not_active_or_occupied(
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    rack_level_slot_output = db_rack_level_slots.results[2]
    rack_level_slot_object = await if_exists(
        RackLevelSlot, "id", rack_level_slot_output.id, async_session
    )
    rack_level_slot_object.is_active = False
    async_session.add(rack_level_slot_object)
    await async_session.commit()
    
    
    with pytest.raises(ServiceException):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[None],
        rack_level_slots_ids=[rack_level_slot_object.id],
        product_counts=[product_count],
        products=[product]
        )


@pytest.mark.asyncio
async def test_raise_exception_when_rack_level_object_do_not_have_enough_available_weight_for_new_stock(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1, max_weight=4
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    with pytest.raises(NotEnoughRackLevelResourcesException):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[None],
        rack_level_slots_ids=[rack_level_object.rack_level_slots[0].id],
        product_counts=[product_count],
        products=[product]
        )


@pytest.mark.asyncio
async def test_raise_exception_when_provided_nonexistent_rack_level_id(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    with pytest.raises(DoesNotExist):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[generate_uuid()],
        rack_level_slots_ids=[None],
        product_counts=[product_count],
        products=[product]
        )


@pytest.mark.asyncio
async def test_raise_exception_when_rack_level_does_not_have_enough_available_slots_for_new_stocks(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1, max_slots=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    rack_level_object.available_slots = 0
    async_session.add(rack_level_object)
    await async_session.commit()
    
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    with pytest.raises(NotEnoughRackLevelResourcesException):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[rack_level_object.id],
        rack_level_slots_ids=[None],
        product_counts=[product_count],
        products=[product]
        )



@pytest.mark.asyncio
async def test_raise_exception_when_rack_level_does_not_have_enough_available_weight_for_new_stocks(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1, max_weight=4
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )

    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    with pytest.raises(NotEnoughRackLevelResourcesException):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[rack_level_object.id],
        rack_level_slots_ids=[None],
        product_counts=[product_count],
        products=[product]
        )

@pytest.mark.asyncio
async def test_raise_exception_when_rack_level_does_not_have_active_or_not_occupied_slots_for_new_slots(
    async_session: AsyncSession,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_staff_user: UserOutputSchema,
):
    rack_input = RackInputSchemaFactory().generate(section_id=db_sections.results[0].id)
    rack_output = await create_rack(async_session, rack_input)

    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=rack_output.id, rack_level_number=1, max_slots=1
    )
    rack_level_output = await create_rack_level(async_session, rack_level_input)
    rack_level_object = await if_exists(
        RackLevel, "id", rack_level_output.id, async_session
    )
    rack_level_object.rack_level_slots[0].is_active = False
    async_session.add(rack_level_object)
    await async_session.commit()
    
    product_count = 5
    product = await if_exists(
        Product, "id", db_products.results[0].id, async_session
    )
    
    with pytest.raises(NoAvailableRackLevelSlotException):
        await create_stocks(
        async_session,
        user_id=db_staff_user.id,
        waiting_rooms_ids=[None],
        rack_level_ids=[rack_level_object.id],
        rack_level_slots_ids=[None],
        product_counts=[product_count],
        products=[product]
        )


