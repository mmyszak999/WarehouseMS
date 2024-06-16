import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.sections.schemas import SectionOutputSchema
from src.apps.stocks.schemas.stock_schemas import StockOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.apps.warehouse.schemas import WarehouseOutputSchema
from src.core.factory.section_factory import (
    SectionInputSchemaFactory,
    SectionUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_products.conftest import db_categories, db_products
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
async def test_only_staff_can_create_section(
    async_client: AsyncClient,
    db_warehouse: PagedResponseSchema[WarehouseOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    section_input = SectionInputSchemaFactory().generate()
    response = await async_client.post(
        "sections/", headers=user_headers, content=section_input.json()
    )
    assert response.status_code == status_code

    if status_code == status.HTTP_201_CREATED:
        assert response.json()["section_name"] == section_input.section_name


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
async def test_authenticated_user_can_get_all_sections(
    async_client: AsyncClient,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("sections/", headers=user_headers)
    assert response.status_code == status_code
    assert response.json()["results"][0]["id"] == db_sections.results[0].id


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
async def test_only_authenticated_user_get_single_section(
    async_client: AsyncClient,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"sections/{db_sections.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json()["id"] == db_sections.results[0].id


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
async def test_only_staff_can_get_update_single_section(
    async_client: AsyncClient,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    section_input = SectionUpdateSchemaFactory().generate(max_racks=77)
    response = await async_client.patch(
        f"sections/{db_sections.results[0].id}",
        headers=user_headers,
        content=section_input.json(),
    )
    assert response.status_code == status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json()["max_racks"] == section_input.max_racks


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
async def test_only_staff_can_get_delete_single_section(
    async_client: AsyncClient,
    db_sections: PagedResponseSchema[SectionOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.delete(
        f"sections/{db_sections.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code
