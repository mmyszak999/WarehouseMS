import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.users.schemas import UserLoginInputSchema, UserOutputSchema
from src.core.factory.user_factory import (
    UserInputSchemaFactory,
    UserUpdateSchemaFactory,
)
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    PASSWORD_SCHEMA,
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_staff_can_create_new_user_account(
    async_client: AsyncClient,
    staff_auth_headers: dict[str, str],
    db_staff_user: UserOutputSchema,
):
    user_input_data = UserInputSchemaFactory().generate()
    response = await async_client.post(
        "users/create", content=user_input_data.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == user_input_data.email


@pytest.mark.asyncio
async def test_authenticated_user_cannot_create_new_user_account(
    async_client: AsyncClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    user_input_data = UserInputSchemaFactory().generate()
    response = await async_client.post(
        "users/create", content=user_input_data.json(), headers=auth_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_anonymous_user_cannot_create_new_user_account(
    async_client: AsyncClient,
):
    user_input_data = UserInputSchemaFactory().generate()
    response = await async_client.post("users/create", content=user_input_data.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_if_user_was_logged_correctly(
    async_client: AsyncClient, db_user: UserOutputSchema
):
    login_data = UserLoginInputSchema(
        email=DB_USER_SCHEMA.email, password=PASSWORD_SCHEMA.password
    )
    response = await async_client.post("users/login", content=login_data.json())
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


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
async def test_staff_and_authenticated_user_can_get_active_users(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("users/", headers=user_headers)

    assert response.status_code == status_code
    assert response.json()["total"] == 2


@pytest.mark.asyncio
async def test_anonymous_user_cannot_get_active_users(
    async_client: AsyncClient,
):
    user_input_data = UserInputSchemaFactory().generate()
    response = await async_client.get("users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_authenticated_user_can_get_their_profile(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = await async_client.get(f"users/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_user.id


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
        (None, None, status.HTTP_401_UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_get_all_users(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get("users/all", headers=user_headers)

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
async def test_authenticated_user_can_get_their_stock_activity_history(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
):
    response = await async_client.get(f"users/{user.id}/history", headers=user_headers)

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
        (None, None, status.HTTP_401_UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_and_authenticated_user_can_get_single_user(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_user: UserOutputSchema,
):
    response = await async_client.get(f"users/{db_user.id}", headers=user_headers)

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
        (None, None, status.HTTP_401_UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_update_single_user(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_user: UserOutputSchema,
):
    update_data = UserUpdateSchemaFactory().generate(first_name="updated")
    response = await async_client.patch(
        f"users/{db_user.id}", headers=user_headers, content=update_data.json()
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
        (None, None, status.HTTP_401_UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_deactivate_single_user(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_user: UserOutputSchema,
):
    response = await async_client.patch(
        f"users/{db_user.id}/deactivate", headers=user_headers
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
        (None, None, status.HTTP_401_UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio
async def test_only_staff_user_can_activate_single_user(
    async_client: AsyncClient,
    user: UserOutputSchema,
    user_headers: dict[str, str],
    status_code: int,
    db_user: UserOutputSchema,
):
    """user deactivation"""
    response = await async_client.patch(
        f"users/{db_user.id}/deactivate", headers=user_headers
    )

    assert response.status_code == status_code

    """user activation"""
    response = await async_client.patch(
        f"users/{db_user.id}/activate", headers=user_headers
    )

    assert response.status_code == status_code
