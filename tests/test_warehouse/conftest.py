import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.warehouse.schemas import WarehouseOutputSchema, WarehouseInputSchema
from src.apps.warehouse.services import create_warehouse, get_all_warehouses
from src.core.factory.warehouse_factory import WarehouseInputSchemaFactory
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


@pytest_asyncio.fixture
async def db_warehouse(
    async_session: AsyncSession
) -> PagedResponseSchema[WarehouseOutputSchema]:
    warehouse_input = WarehouseInputSchemaFactory().generate()
    warehouse = await create_warehouse(
        async_session, warehouse_input
    )
    return await get_all_warehouses(async_session, PageParams())
