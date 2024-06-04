import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


from src.apps.waiting_rooms.schemas import WaitingRoomOutputSchema
from src.apps.waiting_rooms.services import create_waiting_room, get_all_waiting_rooms
from src.core.factory.waiting_room_factory import WaitingRoomInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)


DB_WAITING_ROOMS_SCHEMAS = [WaitingRoomInputSchemaFactory().generate() for _ in range(3)]


@pytest_asyncio.fixture
async def db_waiting_rooms(
    async_session: AsyncSession,
) -> PagedResponseSchema[WaitingRoomOutputSchema]:
    [
        await create_waiting_room(async_session, waiting_room) for waiting_room in DB_WAITING_ROOMS_SCHEMAS
    ]
    return await get_all_waiting_rooms(async_session, PageParams())