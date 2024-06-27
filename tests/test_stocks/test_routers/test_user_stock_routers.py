import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.issues.schemas import IssueOutputSchema
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.stocks.schemas.user_stock_schemas import UserStockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_issues.conftest import db_issues
from tests.test_receptions.conftest import db_receptions
from tests.test_stocks.conftest import db_stocks, db_user_stocks
from tests.test_sections.conftest import db_sections
from tests.test_warehouse.conftest import db_warehouse
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
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_user_with_permission_can_get_all_user_stocks(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_user_stocks: PagedResponseSchema[UserStockOutputSchema],
):
    response = await async_client.get("user-stocks/", headers=user_headers)

    assert response.status_code == status_code
    if response.status_code == status.HTTP_200_OK:
        assert db_user_stocks.total == response.json()["total"]


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
async def test_only_user_with_permission_can_get_single_user_stock(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_user_stocks: PagedResponseSchema[UserStockOutputSchema],
):
    response = await async_client.get(
        f"user-stocks/{db_user_stocks.results[0].id}", headers=user_headers
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert db_user_stocks.results[0].id == response.json()["id"]
