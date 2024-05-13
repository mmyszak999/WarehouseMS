
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table, select


async def if_exists(model_class: Table, field: str, value: Any, session: AsyncSession):
    return await session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )