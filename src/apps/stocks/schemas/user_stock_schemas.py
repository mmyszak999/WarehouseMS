from typing import Optional

from pydantic import BaseModel

from src.apps.issues.schemas import IssueBasicOutputSchema
from src.apps.stocks.schemas.stock_schemas import StockBasicOutputSchema
from src.apps.users.schemas import UserInfoOutputSchema
from src.apps.waiting_rooms.schemas import WaitingRoomBasicOutputSchema


class UserStockInputSchema(BaseModel):
    user_id: str
    stock_id: str
    from_waiting_room_id: Optional[str]
    to_waiting_room_id: Optional[str]
    issue_id: Optional[str]


class UserStockOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    stock: StockBasicOutputSchema
    from_waiting_room: Optional[WaitingRoomBasicOutputSchema]
    to_waiting_room: Optional[WaitingRoomBasicOutputSchema]
    issue: Optional[IssueBasicOutputSchema]

    class Config:
        orm_mode = True
