import pytest
import pytest_asyncio
import asyncio
from asyncio import AbstractEventLoop

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.event import listens_for

from main import app
from src.settings.db_settings import settings
from src.settings.alembic import *
from src.dependencies.get_db import get_db
from src.database.db_connection import Base



@pytest.fixture(scope="session", autouse=True)
def meta_migration():
    sync_engine = create_engine(settings.test_sync_postgres_url, echo=False)

    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)

    yield sync_engine

    Base.metadata.drop_all(sync_engine)


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    engine = create_async_engine(settings.test_postgres_url, echo=False)

    yield engine


@pytest_asyncio.fixture
async def async_session(async_engine: AsyncEngine) -> AsyncSession:
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()

        async_session = AsyncSession(conn, expire_on_commit=False)

        @listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session, transaction):
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                conn.sync_connection.begin_nested()

        yield async_session

        await async_session.close()
        await async_session.rollback()


@pytest.fixture()
def async_client(session: AsyncSession) -> AsyncClient:
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(app=app, base_url="http://test:8000/api/v1")
    del app.dependency_overrides[get_db]