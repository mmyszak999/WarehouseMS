import pytest
from fastapi import BackgroundTasks, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.schemas import (
    UserLoginInputSchema,
    UserOutputSchema,
    UserPasswordSchema,
)
from src.apps.users.services.activation_services import (
    activate_account_service,
    activate_single_user,
    deactivate_single_user,
    manage_activation_status,
    set_user_password,
)
from src.apps.users.services.user_services import (
    authenticate,
    create_single_user,
    create_user_base,
    delete_single_user,
    get_all_users,
    get_single_user,
    update_single_user,
)
from src.core.exceptions import (
    AccountAlreadyActivatedException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    DoesNotExist,
    PasswordAlreadySetException,
    PasswordNotSetException,
    UserCantActivateTheirAccountException,
    UserCantDeactivateTheirAccountException,
)
from src.core.factories import UserInputSchemaFactory, UserUpdateSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.orm import if_exists
from src.core.utils.utils import generate_uuid
from tests.test_users.conftest import (
    DB_USER_SCHEMA,
    PASSWORD_SCHEMA,
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_activation_status_cant_be_changed_for_nonexistent_user(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        await manage_activation_status(async_session, "email", "nosuch@mail.com")


@pytest.mark.asyncio
async def test_activated_account_cant_be_activated_second_time(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    with pytest.raises(AccountAlreadyActivatedException):
        await manage_activation_status(async_session, "email", db_user.email)


@pytest.mark.asyncio
async def test_deactivated_account_cant_be_deactivated_second_time(
    async_session: AsyncSession,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
):
    await deactivate_single_user(async_session, db_user.id, db_staff_user.id)

    with pytest.raises(AccountAlreadyDeactivatedException):
        await manage_activation_status(
            async_session, "email", db_user.email, activate=False
        )


@pytest.mark.asyncio
async def test_user_cant_activate_their_account(
    async_session: AsyncSession,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
):
    await deactivate_single_user(async_session, db_user.id, db_staff_user.id)

    with pytest.raises(UserCantActivateTheirAccountException):
        await activate_single_user(async_session, db_user.email, db_user.email)


@pytest.mark.asyncio
async def test_user_cant_deactivate_their_account(
    async_session: AsyncSession,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(UserCantDeactivateTheirAccountException):
        await deactivate_single_user(async_session, db_user.email, db_user.email)


@pytest.mark.asyncio
async def test_password_cant_be_set_to_nonexistent_user(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    password_schema = UserPasswordSchema(
        password="password", password_repeat="password"
    )
    with pytest.raises(DoesNotExist):
        await set_user_password(async_session, "nosuch@mail.com", password_schema)


@pytest.mark.asyncio
async def test_password_cant_be_set_second_time(
    async_session: AsyncSession, db_user: UserOutputSchema
):
    password_schema = UserPasswordSchema(
        password="password", password_repeat="password"
    )
    with pytest.raises(PasswordAlreadySetException):
        await set_user_password(async_session, db_user.email, password_schema)
