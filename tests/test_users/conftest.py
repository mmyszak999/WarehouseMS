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
    await async_session.refresh()

    return UserOutputSchema.from_orm(new_user)


@pytest.fixture(scope="session", autouse=True)
def create_superuser():
    subprocess.run(["./app_scripts/create_superuser.sh", "test_db"])


@pytest.fixture
def db_user(async_session: AsyncSession) -> UserOutputSchema:
    return register_user_without_activation(sync_session, DB_USER_SCHEMA)


@pytest.fixture
def db_staff_user(async_session: AsyncSession) -> UserOutputSchema:
    return register_user_without_activation(
        sync_session, DB_STAFF_USER_SCHEMA, is_staff=True
    )


@pytest.fixture
def auth_headers(async_session: AsyncSession, db_user: UserOutputSchema) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(db_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def staff_auth_headers(
    async_session: AsyncSession, db_staff_user: UserOutputSchema
) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(db_staff_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def superuser_auth_headers(sync_session: AsyncSession) -> dict[str, str]:
    access_token = AuthJWT().create_access_token("superuser@mail.com")
    return {"Authorization": f"Bearer {access_token}"}