import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.issues.schemas import IssueOutputSchema
from src.apps.stocks.models import Stock
from src.apps.stocks.schemas.stock_schemas import (
    StockIssueInputSchema,
    StockOutputSchema,
)
from src.apps.users.schemas import UserOutputSchema
from src.core.factory.issue_factory import (
    IssueInputSchemaFactory,
    IssueUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.orm import if_exists
from tests.test_issues.conftest import db_issues
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
async def test_only_user_with_proper_permission_can_create_issue(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
):
    available_stocks = [stock for stock in db_stocks.results if not stock.is_issued]
    issue_input = IssueInputSchemaFactory().generate(
        stock_ids=[StockIssueInputSchema(id=available_stocks[0].id)]
    )
    response = await async_client.post(
        "issues/", headers=user_headers, content=issue_input.json()
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
async def test_only_user_with_proper_permission_can_get_all_issues(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):

    response = await async_client.get("issues/", headers=user_headers)

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert db_issues.total == response.json()["total"]


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
async def test_only_user_with_proper_permission_can_get_single_issue(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    response = await async_client.get(
        f"issues/{db_issues.results[0].id}", headers=user_headers
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert db_issues.results[0].id == response.json()["id"]


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
async def test_only_user_with_proper_permission_can_update_single_issue(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
):
    update_data = IssueUpdateSchemaFactory().generate(description="wow")
    response = await async_client.patch(
        f"issues/{db_issues.results[0].id}",
        headers=user_headers,
        content=update_data.json(),
    )

    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert update_data.description == response.json()["description"]
