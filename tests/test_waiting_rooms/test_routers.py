import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.waiting_rooms.schemas import WaitingRoomOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.stocks.schemas import StockOutputSchema, StockWaitingRoomInputSchema
from src.apps.users.schemas import UserOutputSchema
from src.apps.issues.schemas import IssueOutputSchema
from src.core.factory.waiting_room_factory import (
    WaitingRoomUpdateSchemaFactory,
    WaitingRoomInputSchemaFactory
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_issues.conftest import db_issues
from tests.test_products.conftest import db_products, db_categories
from tests.test_receptions.conftest import db_receptions
from tests.test_stocks.conftest import db_stocks
from tests.test_waiting_rooms.conftest import db_waiting_rooms
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


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
            status.HTTP_201_CREATED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_user_with_proper_permission_can_create_waiting_room(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema]
):
    waiting_room_data = WaitingRoomInputSchemaFactory().generate(
        max_stocks=10, max_weight=1000
    )
    response = await async_client.post(
        "waiting_rooms/", headers=user_headers, content=waiting_room_data.json()
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_201_CREATED:
        assert response.json()["max_stocks"] == waiting_room_data.max_stocks


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
async def test_authenticated_user_can_get_waiting_rooms(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    response = await async_client.get(
        "waiting_rooms/", headers=user_headers
    )
    assert response.status_code == status_code
    assert response.json()["total"] == db_waiting_rooms.total


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
async def test_authenticated_can_get_single_waiting_room(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    response = await async_client.get(
        f"waiting_rooms/{db_waiting_rooms.results[1].id}", headers=user_headers
    )
    assert response.status_code == status_code
    assert response.json()["id"] == db_waiting_rooms.results[1].id


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
async def test_only_user_with_proper_permission_can_update_waiting_room(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    update_data = WaitingRoomUpdateSchemaFactory().generate(
        max_stocks=1111
    )
    response = await async_client.patch(
        f"waiting_rooms/{db_waiting_rooms.results[1].id}", headers=user_headers,
        content=update_data.json()
    )
    assert response.status_code == status_code
    if response.status_code == status.HTTP_200_OK:
        assert response.json()["id"] == db_waiting_rooms.results[1].id


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
            status.HTTP_204_NO_CONTENT,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_user_with_proper_permission_can_delete_waiting_room(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    response = await async_client.delete(
        f"waiting_rooms/{db_waiting_rooms.results[2].id}", headers=user_headers
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
async def test_only_user_with_proper_permission_can_add_stock_to_waiting_room(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_waiting_rooms: PagedResponseSchema[WaitingRoomOutputSchema],
):
    stock_data = StockWaitingRoomInputSchema(id=db_stocks.results[0].id)
    response = await async_client.patch(
        f"waiting_rooms/{db_waiting_rooms.results[2].id}/add-stock", headers=user_headers,
        content=stock_data.json()
    )
    assert response.status_code == status_code