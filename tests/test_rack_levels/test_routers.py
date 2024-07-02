import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.rack_levels.schemas import RackLevelOutputSchema
from src.apps.racks.schemas import RackOutputSchema
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.factory.rack_level_factory import (
    RackLevelInputSchemaFactory,
    RackLevelUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_products.conftest import db_categories, db_products
from tests.test_rack_levels.conftest import db_rack_levels
from tests.test_racks.conftest import db_racks
from tests.test_sections.conftest import db_sections
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_warehouse.conftest import db_warehouse


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
async def test_only_staff_can_create_rack(
    async_client: AsyncClient,
    db_racks: PagedResponseSchema[RackOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    rack_level_input = RackLevelInputSchemaFactory().generate(
        rack_id=db_racks.results[0].id, rack_level_number=db_racks.results[0].max_levels
    )
    response = await async_client.post(
        "rack_levels/", headers=user_headers, content=rack_level_input.json()
    )
    assert response.status_code == status_code

    if status_code == status.HTTP_201_CREATED:
        assert (
            response.json()["rack_level_number"] == rack_level_input.rack_level_number
        )


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
async def test_authenticated_user_can_get_single_rack_level(
    async_client: AsyncClient,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"rack_levels/{db_rack_levels.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code
    assert response.json()["id"] == db_rack_levels.results[0].id


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
async def test_authenticated_user_can_get_all_rack_levels(
    async_client: AsyncClient,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("rack_levels/", headers=user_headers)
    assert response.status_code == status_code
    assert response.json()["total"] == db_rack_levels.total


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
async def test_only_staff_can_update_single_rack_level(
    async_client: AsyncClient,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    rack_level_input = RackLevelUpdateSchemaFactory().generate(max_weight=2)
    response = await async_client.patch(
        f"rack_levels/{db_rack_levels.results[0].id}",
        headers=user_headers,
        content=rack_level_input.json(),
    )
    assert response.status_code == status_code

    if status_code == status.HTTP_200_OK:
        assert response.json()["max_weight"] == rack_level_input.max_weight


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
async def test_only_staff_can_delete_single_rack_level(
    async_client: AsyncClient,
    db_rack_levels: PagedResponseSchema[RackLevelOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.delete(
        f"rack_levels/{db_rack_levels.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code
