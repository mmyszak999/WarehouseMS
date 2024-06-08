from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.models import Product
from src.apps.users.models import User
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.stocks.models import Stock, UserStock
from src.apps.stocks.schemas.user_stock_schemas import (
    UserStockInputSchema,
    UserStockOutputSchema
)
from src.apps.waiting_rooms.models import WaitingRoom
from src.apps.waiting_rooms.services import manage_waiting_room_state
from src.core.exceptions import (
    AlreadyExists,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    MissingProductDataException,
    NoAvailableWaitingRoomsException,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.orm import if_exists
from src.core.utils.time import get_current_time


async def create_user_stock_object(
    session: AsyncSession,
    stock_id: str,
    user_id: str,
    to_waiting_room_id: str
) -> UserStockOutputSchema:
    if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
        raise DoesNotExist(Stock.__name__, "id", stock_id)
    
    if not (user_object := await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)
    
    if not (waiting_room_object := await if_exists(WaitingRoom, "id", to_waiting_room_id, session)):
        raise DoesNotExist(WaitingRoom.__name__, "id", to_waiting_room_id)
    
    input_schema = UserStockInputSchema(
        user_id=user_id,
        stock_id=stock_id,
        to_waiting_room_id=to_waiting_room_id
    )
    
    new_user_stock = UserStock(**input_schema.dict())
    session.add(new_user_stock)
    await session.flush()
    print(new_user_stock.__dict__)
    return UserStockOutputSchema.from_orm(new_user_stock)


async def get_single_user_stock(
    session: AsyncSession, user_stock_id: int) -> UserStockOutputSchema:
    if not (user_stock_object := await if_exists(UserStock, "id", user_stock_id, session)):
        raise DoesNotExist(UserStock.__name__, "id", user_stock_id)

    return UserStockOutputSchema.from_orm(user_stock_object)


async def get_multiple_user_stocks(
    session: AsyncSession,
    page_params: PageParams,
    stock_id: str = None,
    user_id: str = None
) -> PagedResponseSchema[UserStockOutputSchema]:
    query = select(UserStock)
    if stock_id is not None:
        if not (stock_object := await if_exists(Stock, "id", stock_id, session)):
            raise DoesNotExist(Stock.__name__, "id", stock_id)
        query = query.filter(UserStock.stock_id == stock_id)
    
    if user_id is not None:
        if not (user_object := await if_exists(User, "id", user_id, session)):
            raise DoesNotExist(User.__name__, "id", user_id)
        query = query.filter(UserStock.user_id == user_id)

    return await paginate(
        query=query,
        response_schema=UserStockOutputSchema,
        table=UserStock,
        page_params=page_params,
        session=session,
    )


async def get_all_user_stocks(
    session: AsyncSession, page_params: PageParams
) -> PagedResponseSchema[UserStockOutputSchema]:
    return await get_multiple_user_stocks(session, page_params)


async def get_all_user_stocks_with_single_user_involvement(
    session: AsyncSession, page_params: PageParams, user_id: str
) -> PagedResponseSchema[UserStockOutputSchema]:
    return await get_multiple_user_stocks(session, page_params, user_id=user_id)


async def get_all_user_stock_history_for_single_stock(
    session: AsyncSession, page_params: PageParams, stock_id: str
) -> PagedResponseSchema[UserStockOutputSchema]:
    return await get_multiple_user_stocks(session, page_params, stock_id=stock_id)