import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.products.schemas.category_schemas import CategoryOutputSchema
from src.apps.users.schemas import UserOutputSchema
from src.core.factory.category_factory import CategoryInputSchemaFactory, CategoryUpdateSchemaFactory
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_products.conftest import db_categories
from src.core.pagination.schemas import PagedResponseSchema


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
    status_code: int,
):
    category_data = ProductInputSchemaFactory().generate()
    response = await async_client.post(
        "categories/",
        headers=user_headers,
        content=category_data.json())

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
        )
    ],
)
@pytest.mark.asyncio
async def test_staff_and_authenticated_user_can_get_all_categories(
    async_client: AsyncClient,
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        "categories/",
        headers=user_headers
    )

    assert response.status_code == status_code
    assert response.json()["total"] == 3


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
        (
            None,
            None,
            status.HTTP_401_UNAUTHORIZED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_get_single_category(
    async_client: AsyncClient,
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(
        f"categories/{db_categories.results[0].id}",
        headers=user_headers
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
        (
            None,
            None,
            status.HTTP_401_UNAUTHORIZED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_update_single_category(
    async_client: AsyncClient,
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    update_schema = CategoryUpdateSchemaFactory().generate(name="test_name")
    response = await async_client.patch(
        f"categories/{db_categories.results[0].id}",
        headers=user_headers,
        content=update_schema.json()
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
            status.HTTP_204_NO_CONTENT,
        ),
        (
            None,
            None,
            status.HTTP_401_UNAUTHORIZED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_delete_single_category(
    async_client: AsyncClient,
    db_categories: PagedResponseSchema[CategoryOutputSchema],
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.delete(
        f"categories/{db_categories.results[0].id}",
        headers=user_headers
    )

    assert response.status_code == status_code