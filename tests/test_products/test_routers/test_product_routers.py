import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.products.schemas.category_schemas import CategoryOutputSchema, CategoryIdListSchema
from src.apps.products.schemas.product_schemas import ProductOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.factory.product_factory import ProductInputSchemaFactory, ProductUpdateSchemaFactory
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_products.conftest import db_categories, db_products


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
async def test_only_staff_user_can_create_product(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    product_data = ProductInputSchemaFactory().generate(
        category_ids=CategoryIdListSchema(id=[db_categories.results[0].id])
    )
    response = await async_client.post(
        "products/", content=product_data.json(), headers=user_headers
    )
    assert response.status_code == status_code


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
async def test_staff_and_authenticated_user_can_get_all_available_products(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    response = await async_client.get(
        "products/", headers=user_headers
    )
    assert response.status_code == status_code
    assert response.json()["total"] == db_products.total


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
async def test_only_staff_user_can_get_all_product_including_legacy_ones(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    response = await async_client.get(
        "products/all", headers=user_headers
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
async def test_only_staff_user_can_get_all_data_about_single_product(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    response = await async_client.get(
        f"products/all/{db_products.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code


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
async def test_only_staff_and_authenticated_user_can_get_basic_data_about_single_product(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    response = await async_client.get(
        f"products/{db_products.results[0].id}", headers=user_headers
    )
    assert response.status_code == status_code
    assert response.json()["id"] == db_products.results[0].id


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
async def test_only_staff_user_can_update_single_product(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    update_data = ProductUpdateSchemaFactory().generate(name="test_name")
    response = await async_client.patch(
        f"products/{db_products.results[0].id}", headers=user_headers,
        content=update_data.json()
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
async def test_only_staff_user_can_make_single_product_legacy(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    db_products: PagedResponseSchema[ProductOutputSchema],
    status_code: int,
    db_categories: PagedResponseSchema[CategoryOutputSchema]
):
    response = await async_client.patch(
        f"products/{db_products.results[0].id}/legacy", headers=user_headers
    )
    assert response.status_code == status_code