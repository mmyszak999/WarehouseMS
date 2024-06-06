import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.issues.schemas import IssueOutputSchema
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.stocks.schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_issues.conftest import db_issues
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
async def test_only_authenticated_user_can_get_available_stocks(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):

    response = await async_client.get("stocks/", headers=user_headers)

    assert response.status_code == status_code
    assert db_receptions.total - 1 == response.json()["total"]


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
async def test_only_staff_user_can_get_all_stocks(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_products: PagedResponseSchema[ProductOutputSchema],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    response = await async_client.get("stocks/all", headers=user_headers)

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert db_stocks.total == response.json()["total"]


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
async def test_only_staff_user_can_get_all_data_about_single_stock(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):

    response = await async_client.get(
        f"stocks/all/{db_stocks.results[0].id}", headers=user_headers
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert db_stocks.results[0].id == response.json()["id"]


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
async def test_only_authenticated_user_can_get_basic_data_about_single_stock(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]   
    response = await async_client.get(
        f"stocks/{available_stocks[0].id}", headers=user_headers
    )
    print(response.json())

    assert response.status_code == status_code
    assert available_stocks[0].id == response.json()["id"]
