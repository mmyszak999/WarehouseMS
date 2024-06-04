import uuid
from typing import Any

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession


async def if_exists(model_class: Table, field: str, value: Any, session: AsyncSession):
    return await session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )


def default_available_slots(context):
    return context.get_current_parameters()["max_stocks"]


def default_available_stock_weight(context):
    return context.get_current_parameters()["max_weight"]
