"""import pytest
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient, Response

from src.apps.users.schemas import (
    UserInputSchema,
    UserLoginInputSchema,
    UserOutputSchema,
    UserPasswordSchema,
)
from src.core.factory.user_factory import (
    UserInputSchemaFactory,
    UserUpdateSchemaFactory,
)
from src.core.utils.email import generate_confirm_token
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    PASSWORD_SCHEMA,
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_user_can_succesfully_activate_their_account_via_activation_link(
    async_client: AsyncClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
):
    create_data = UserInputSchemaFactory().generate()
    response = await async_client.post(
        "users/create", content=create_data.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["is_active"] == False

    token = await generate_confirm_token([create_data.email])
    user_passwords = UserPasswordSchema(password="password", password_repeat="password")
    response = await async_client.post(
        f"email/confirm-account-activation/{token}", content=user_passwords.json()
    )
    assert response.status_code == status.HTTP_200_OK

    activated_user_token = AuthJWT().create_access_token(create_data.email)
    activated_user_auth_headers = {"Authorization": f"Bearer {activated_user_token}"}

    response = await async_client.get("users/me", headers=activated_user_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] == True
    assert response.json()["email"] == create_data.email
"""