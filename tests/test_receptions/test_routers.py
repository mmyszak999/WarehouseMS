import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.factory.reception_factory import (
    ReceptionInputSchemaFactory,
    ReceptionProductInputSchemaFactory,
    ReceptionUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_issues.conftest import db_issues
from tests.test_products.conftest import db_products
from tests.test_receptions.conftest import db_receptions
from tests.test_stocks.conftest import db_stocks
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
async def test_only_user_with_proper_permission_can_create_reception(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):
    reception_data = ReceptionInputSchemaFactory().generate(
        products_data=[
            ReceptionProductInputSchemaFactory().generate(db_products.results[0].id, 5)
        ]
    )
    response = await async_client.post(
        "receptions/", headers=user_headers, content=reception_data.json()
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert response.json()["user"]["id"] == user.id


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
async def test_only_user_with_proper_permission_can_get_all_receptions(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):

    response = await async_client.get("receptions/", headers=user_headers)

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert db_receptions.total == response.json()["total"]


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
async def test_only_user_with_proper_permission_can_get_single_reception(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):

    response = await async_client.get(
        f"receptions/{db_receptions.results[0].id}", headers=user_headers
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert db_receptions.results[0].id == response.json()["id"]


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
async def test_only_user_with_proper_permission_can_update_single_reception(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
):
    update_data = ReceptionUpdateSchemaFactory().generate(description="wow")
    response = await async_client.patch(
        f"receptions/{db_receptions.results[0].id}",
        headers=user_headers,
        content=update_data.json(),
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert update_data.description == response.json()["description"]
