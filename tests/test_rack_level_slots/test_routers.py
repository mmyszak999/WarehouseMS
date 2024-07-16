import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.rack_level_slots.schemas import RackLevelSlotOutputSchema
from src.apps.racks.schemas import RackOutputSchema
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.stocks.schemas.stock_schemas import (
    StockOutputSchema,
    StockRackLevelInputSchema,
)
from src.apps.users.schemas import UserOutputSchema
from src.core.factory.rack_level_slot_factory import (
    RackLevelSlotInputSchemaFactory,
    RackLevelSlotUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_products.conftest import db_categories, db_products
from tests.test_rack_levels.conftest import db_rack_levels
from tests.test_racks.conftest import db_racks
from tests.test_sections.conftest import db_sections
from tests.test_stocks.conftest import db_stocks
from tests.test_rack_level_slots.conftest import db_rack_level_slots
from src.core.utils.orm import if_exists
from src.apps.rack_level_slots.models import RackLevelSlot
from src.apps.stocks.schemas.stock_schemas import StockRackLevelSlotInputSchema
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_warehouse.conftest import db_warehouse
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from src.apps.waiting_rooms.schemas import WaitingRoomOutputSchema


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_authenticated_user_can_get_single_rack_level_slot(
    async_client: AsyncClient,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"rack-level-slots/{db_rack_level_slots.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code
    assert response.json()["id"] == db_rack_level_slots.results[0].id


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_authenticated_user_can_get_all_rack_level_slots(
    async_client: AsyncClient,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("rack-level-slots/", headers=user_headers)
    assert response.status_code == status_code
    assert response.json()["total"] == db_rack_level_slots.total


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_can_update_single_rack_level_slot(
    async_client: AsyncClient,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    rack_level_slot_input = RackLevelSlotUpdateSchemaFactory().generate(description="testt")
    response = await async_client.patch(
        f"rack-level-slots/{db_rack_level_slots.results[0].id}",
        headers=user_headers,
        content=rack_level_slot_input.json(),
    )
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        assert response.json()["description"] == rack_level_slot_input.description


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_can_deactivate_single_rack_level_slot(
    async_client: AsyncClient,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.patch(
        f"rack-level-slots/{db_rack_level_slots.results[0].id}/deactivate", headers=user_headers
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_can_activate_single_rack_level_slot(
    async_client: AsyncClient,
    async_session: AsyncSession,
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    rack_level_slot_object = await if_exists(
        RackLevelSlot, "id", db_rack_level_slots.results[-1].id, async_session
    )
    rack_level_slot_object.is_active = False
    async_session.add(rack_level_slot_object)
    await async_session.commit()
    
    response = await async_client.patch(
        f"rack-level-slots/{rack_level_slot_object.id}/activate", headers=user_headers
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user, user_headers, status_code",
    [
        (
            pytest.lazy_fixture("db_user"),
            pytest.lazy_fixture("auth_headers"),
            status.HTTP_403_FORBIDDEN,
        ),
        (
            pytest.lazy_fixture("db_staff_user"),
            pytest.lazy_fixture("staff_auth_headers"),
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_can_add_single_stock_to_rack_level_slot(
    async_client: AsyncClient,
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
    db_rack_level_slots: PagedResponseSchema[RackLevelSlotOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    waiting_room_with_stocks = [
        waiting_room for waiting_room in db_waiting_rooms.results if waiting_room.stocks
    ]
    
    stock_id_input = StockRackLevelSlotInputSchema(id=waiting_room_with_stocks[0].stocks[0].id)
    response = await async_client.patch(
        f"rack-level-slots/{db_rack_level_slots.results[-1].id}/add-stock",
        headers=user_headers,
        content=stock_id_input.json(),
    )
    assert response.status_code == status_code
