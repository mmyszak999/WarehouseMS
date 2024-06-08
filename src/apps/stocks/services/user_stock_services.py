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
        to_waiting_room=to_waiting_room_id
    )
    
    new_user_stock = UserStock(**input_schema.dict())
    session.add(new_user_stock)
    await session.flush()
    print(new_user_stock.__dict__)
    return UserStockOutputSchema.from_orm(new_user_stock)


    
    


