from typing import Optional

from pydantic import BaseModel

from src.apps.waiting_rooms.schemas import WaitingRoomBasicOutputSchema
from src.apps.users.schemas import UserInfoOutputSchema
from src.apps.stocks.schemas import StockBasicOutputSchema


class UserStockInputSchema(BaseModel):
    user_id: str
    stock_id: str
    from_waiting_room_id: Optional[str]
    to_waiting_room_id: Optional[str]


class UserStockOutputSchema(BaseModel):
    user: UserInfoOutputSchema
    stock: StockBasicOutputSchema
    from_waiting_room: Optional[WaitingRoomBasicOutputSchema]
    to_waiting_room: Optional[WaitingRoomBasicOutputSchema]
