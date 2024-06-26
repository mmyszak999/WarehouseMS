import subprocess

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.apps.users.schemas import UserInputSchema, UserOutputSchema
from src.apps.users.services.activation_services import set_user_password
from src.apps.users.services.user_services import create_user_base
from src.core.factory.user_factory import (
    UserInputSchemaFactory,
    UserPasswordSchemaFactory,
)
from src.core.pagination.models import PageParams

DB_USER_SCHEMA = UserInputSchemaFactory().generate()

DB_STAFF_USER_SCHEMA = UserInputSchemaFactory().generate()

PASSWORD_SCHEMA = UserPasswordSchemaFactory().generate()


async def create_user_without_activation(
    async_session: AsyncSession,
    user_schema: UserInputSchema,
    is_active: bool = True,
    is_staff: bool = False,
    can_move_stocks: bool = False,
    can_recept_stocks: bool = False,
    can_issue_stocks: bool = False,
):
    new_user = await create_user_base(async_session, user_schema)
    new_user.is_active = is_active
    new_user.is_staff = is_staff
    new_user.can_move_stocks = can_move_stocks
    new_user.can_recept_stocks = can_recept_stocks
    new_user.can_issue_stocks = can_issue_stocks
    async_session.add(new_user)

    await set_user_password(async_session, new_user.email, PASSWORD_SCHEMA)
    async_session.add(new_user)

    await async_session.commit()
    await async_session.refresh(new_user)

    return UserOutputSchema.from_orm(new_user)


@pytest.fixture(scope="session", autouse=True)
def create_superuser():
    subprocess.run(["./app_scripts/create_superuser.sh", "test_db"])


@pytest_asyncio.fixture
async def db_user(async_session: AsyncSession) -> UserOutputSchema:
    return await create_user_without_activation(async_session, DB_USER_SCHEMA)


@pytest_asyncio.fixture
async def db_staff_user(async_session: AsyncSession) -> UserOutputSchema:
    return await create_user_without_activation(
        async_session,
        DB_STAFF_USER_SCHEMA,
        is_staff=True,
        can_move_stocks=True,
        can_issue_stocks=True,
        can_recept_stocks=True,
    )


@pytest.fixture
def auth_headers() -> dict[str, str]:
    access_token = AuthJWT().create_access_token(DB_USER_SCHEMA.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def staff_auth_headers() -> dict[str, str]:
    access_token = AuthJWT().create_access_token(DB_STAFF_USER_SCHEMA.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def superuser_auth_headers() -> dict[str, str]:
    access_token = AuthJWT().create_access_token("superuser@mail.com")
    return {"Authorization": f"Bearer {access_token}"}
