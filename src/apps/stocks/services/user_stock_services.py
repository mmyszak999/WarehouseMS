from typing import Union

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.models import Product
from src.apps.stocks.models import Stock, UserStock
from src.apps.stocks.schemas import (
    StockBasicOutputSchema,
    StockInputSchema,
    StockOutputSchema,
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


