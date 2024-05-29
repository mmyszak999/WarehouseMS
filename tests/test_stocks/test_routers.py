import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.stocks.schemas import StockOutputSchema
from src.apps.receptions.schemas import ReceptionOutputSchema
from src.apps.issues.schemas import IssueOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_stocks.conftest import db_stocks
from tests.test_receptions.conftest import db_receptions
from tests.test_issues.conftest import db_issues
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)

@pytest.mark.asyncio
async def test_wow(
    async_client: AsyncClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_receptions: PagedResponseSchema[ReceptionOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema]
):
    
    response = await async_client.get(
        "issues/",  headers=staff_auth_headers
    )
    print(response.json())
    
    
    assert 1 == 2