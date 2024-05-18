import pytest

from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.users.schemas import UserLoginInputSchema, UserOutputSchema
from src.core.factories import UserInputSchemaFactory
from tests.test_users.conftest import DB_USER_SCHEMA


@pytest.mark.asyncio
async def test_if_user_was_created_successfully(
    async_client: AsyncClient,
    staff_auth_headers: dict[str, str],
    db_staff_user: UserOutputSchema
):
    await db_staff_user
    user_input_data = UserInputSchemaFactory().generate()
    response = await async_client.post(
        "users/create",
        content=user_input_data.json(),
        headers=staff_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == user_input_data.email

async def test_if_user_was_logged_correctly(
    sync_client: TestClient, db_user: UserOutputSchema
):
    login_data = UserLoginInputSchema(
        email=DB_USER_SCHEMA.email, password=DB_USER_SCHEMA.password
    )
    response = sync_client.post("users/login", json=login_data.dict())
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()