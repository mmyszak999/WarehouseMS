import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.stocks.schemas.stock_schemas import (
    StockOutputSchema
)
from src.apps.users.schemas import UserOutputSchema
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.core.factory.warehouse_factory import (
    WarehouseInputSchemaFactory,
    WarehouseUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_products.conftest import db_categories, db_products
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
async def test_only_staff_can_create_warehouse(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    warehouse_input = WarehouseInputSchemaFactory().generate()
    response = await async_client.post(
        "warehouse/", headers=user_headers, content=warehouse_input.json()
    )
    assert response.status_code == status_code
    
    if status_code == status.HTTP_201_CREATED:
        assert response.json()["warehouse_name"] == warehouse_input.warehouse_name

@pytest.mark.asyncio
async def test_only_staff_can_create_warehouse(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    warehouse_input = WarehouseInputSchemaFactory().generate()
    response = await async_client.post(
        "warehouse/", headers=user_headers, content=warehouse_input.json()
    )
    assert response.status_code == status_code
    
    if status_code == status.HTTP_201_CREATED:
        assert response.json()["warehouse_name"] == warehouse_input.warehouse_name