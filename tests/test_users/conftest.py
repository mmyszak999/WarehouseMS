import subprocess

import pytest
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from src.apps.users.schemas import (
    UserOutputSchema,
    UserInputSchema
)
from src.apps.users.services.user_services import create_user_base
from src.apps.users.services.activation_services import set_user_password
from src.core.factories import UserInputSchemaFactory, UserPasswordSchemaFactory
from src.core.pagination.models import PageParams


DB_USER_SCHEMA = UserInputSchemaFactory().generate()

DB_STAFF_USER_SCHEMA = UserInputSchemaFactory().generate()

PASSWORD_SCHEMA = UserPasswordSchemaFactory().generate()


async def create_user_without_activation(
    async_session: AsyncSession,
    user_schema: UserInputSchema,
    is_active: bool = True,
    is_staff: bool = False,
    can_move_goods: bool = False, 
    can_recept_goods: bool = False, 
    can_issue_goods: bool = False, 
):
    new_user = await create_user_base(async_session, user_schema)
    new_user.is_active = is_active
    new_user.is_staff = is_staff
    new_user.can_move_goods = can_move_goods
    new_user.can_recept_goods = can_recept_goods 
    new_user.can_issue_goods = can_issue_goods
    async_session.add(new_user)
    
    await set_user_password(async_session, new_user.email, PASSWORD_SCHEMA)
    async_session.add(new_user)
    
    await async_session.commit()
    await async_session.refresh(new_user)

    return UserOutputSchema.from_orm(new_user)


@pytest.fixture(scope="session", autouse=True)
def create_superuser():
    subprocess.run(["./app_scripts/create_superuser.sh", "test_db"])


@pytest.fixture
async def user(async_session: AsyncSession) -> UserOutputSchema:
    """creates basic user"""
    return await create_user_without_activation(async_session, DB_USER_SCHEMA)


@pytest.fixture
async def staff_user(async_session: AsyncSession) -> UserOutputSchema:
    """creates staff user"""
    return await create_user_without_activation(
        async_session, DB_STAFF_USER_SCHEMA, is_staff=True,
        can_move_goods=True, can_issue_goods=True, can_recept_goods=True
    )


@pytest.fixture
async def db_user(async_session: AsyncSession, user) -> UserOutputSchema:
    """awaits coroutine with basic user and hides implementation"""
    return await user


@pytest.fixture
async def db_staff_user(async_session: AsyncSession, staff_user) -> UserOutputSchema:
    """awaits coroutine with staff user and hides implementation"""
    return await staff_user


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