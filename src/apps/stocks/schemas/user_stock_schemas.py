from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from src.apps.issues.schemas import IssueBasicOutputSchema
from src.apps.rack_level_slots.schemas import RackLevelSlotBaseOutputSchema
from src.apps.stocks.schemas.stock_schemas import StockBasicOutputSchema
from src.apps.users.schemas import UserInfoOutputSchema
from src.apps.waiting_rooms.schemas import WaitingRoomBasicOutputSchema
from src.apps.receptions.schemas import ReceptionBasicOutputSchema


class UserStockInputSchema(BaseModel):
    user_id: str
    stock_id: str
    from_waiting_room_id: Optional[str]
    to_waiting_room_id: Optional[str]
    from_rack_level_slot_id: Optional[str]
    to_rack_level_slot_id: Optional[str]
    issue_id: Optional[str]
    reception_id: Optional[str]


class UserStockOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    stock: StockBasicOutputSchema
    from_waiting_room: Optional[WaitingRoomBasicOutputSchema]
    to_waiting_room: Optional[WaitingRoomBasicOutputSchema]
    from_rack_level_slot: Optional[RackLevelSlotBaseOutputSchema]
    to_rack_level_slot: Optional[RackLevelSlotBaseOutputSchema]
    issue: Optional[IssueBasicOutputSchema]
    reception: Optional[ReceptionBasicOutputSchema]
    moved_at: date

    class Config:
        orm_mode = True
