import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.waiting_rooms.schemas import (
    WaitingRoomInputSchema, WaitingRoomOutputSchema, WaitingRoomUpdateSchema
)
from src.apps.waiting_rooms.services import (
    create_waiting_room,
    get_all_waiting_rooms,
    get_single_waiting_room,
    update_single_waiting_room,
    delete_single_waiting_room,
    add_single_stock_to_waiting_room,
    manage_waiting_room_state
)
from src.apps.users.schemas import UserOutputSchema
from src.apps.stocks.schemas import StockOutputSchema, StockWaitingRoomInputSchema
from src.apps.issues.schemas import IssueOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    TooLittleWaitingRoomWeightException,
    ServiceException,
)
from src.core.factory.waiting_room_factory import (
    WaitingRoomUpdateSchemaFactory,
    WaitingRoomInputSchemaFactory
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_issues.conftest import db_issues
from tests.test_products.conftest import db_products, db_categories
from tests.test_receptions.conftest import db_receptions
from tests.test_stocks.conftest import db_stocks
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from src.core.utils.utils import generate_uuid
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_if_only_one_waiting_room_was_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_room = await get_single_waiting_room(async_session, db_waiting_rooms.results[1].id)

    assert waiting_room.id == db_waiting_rooms.results[1].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_waiting_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    with pytest.raises(DoesNotExist):
        await get_single_waiting_room(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_waiting_rooms_were_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    waiting_rooms = await get_all_waiting_rooms(async_session, PageParams(page=1, size=5))
    assert waiting_rooms.total == waiting_rooms.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_waiitng_room(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    update_data = WaitingRoomInputSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_waiting_room(async_session, update_data, generate_uuid())


@pytest.mark.asyncio
async def test_raise_exception_while_requested_max_weight_is_smaller_than_the_current_stock_weight(
    async_session: AsyncSession,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    waiting_room = db_waiting_rooms.results[0]
    update_data = WaitingRoomUpdateSchemaFactory().generate(max_weight=0.00001)
    with pytest.raises(TooLittleWaitingRoomWeightException):
        await update_single_waiting_room(async_session, update_data, waiting_room.id)
