from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field

from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionStockOutputSchema
from src.apps.stocks.schemas import StockBasicOutputSchema, StockIssueInputSchema
from src.apps.users.schemas import UserInfoOutputSchema



class WaitingRoomBaseSchema(BaseModel):
    max_stocks: int
    max_weight: Decimal


class WaitingRoomInputSchema(WaitingRoomBaseSchema):
    pass


class WaitingRoomUpdateSchema(BaseModel):
    max_stocks: Optional[int]
    max_weight: Optional[Decimal]


class WaitingRoomBasicOutputSchema(WaitingRoomBaseSchema):
    id: str
    stocks: list[StockBasicOutputSchema]
    
    
class WaitingRoomcOutputSchema(WaitingRoomBasicOutputSchema):
    occupied_slots: int

