from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.settings.db_settings import settings

engine = create_async_engine(
    settings.postgres_url, echo=False, future=True, pool_size=20, max_overflow=0
)

async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.commit()