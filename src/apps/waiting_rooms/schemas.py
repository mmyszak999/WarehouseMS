from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionStockOutputSchema
from src.apps.stocks.schemas import StockBasicOutputSchema, StockIssueInputSchema
from src.apps.users.schemas import UserInfoOutputSchema



class WaitingRoomBaseSchema(BaseModel):
    max_stocks: int
    max_weight: Decimal
    
    @validator("max_stocks")
    def validate_max_stocks(cls, max_stocks: int) -> int:
        if max_stocks and (max_stocks <= 0):
            raise ValueError("Max stocks must be positive! ")
        return max_stocks

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: int) -> int:
        if max_weight and (max_weight <= 0):
            raise ValueError("Max weight must be positive! ")
        return max_weight
    


class WaitingRoomInputSchema(WaitingRoomBaseSchema):
    pass

    class Config:
        orm_mode = True


class WaitingRoomUpdateSchema(BaseModel):
    max_stocks: Optional[int]
    max_weight: Optional[Decimal]
    
    @validator("max_stocks")
    def validate_max_stocks(cls, max_stocks: int) -> int:
        if max_stocks and (max_stocks < 0):
            raise ValueError("Max stocks must be positive! ")
        return max_stocks

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: int) -> int:
        if max_weight and (max_weight < 0):
            raise ValueError("Max weight must be positive! ")
        return max_weight


class WaitingRoomBasicOutputSchema(WaitingRoomBaseSchema):
    id: str
    stocks: list[StockBasicOutputSchema]
    
    class Config:
        orm_mode = True
    
    
class WaitingRoomOutputSchema(WaitingRoomBasicOutputSchema):
    occupied_slots: int
    available_slots: int
    current_stock_weight: Decimal
    available_stock_weight: Decimal
    
    class Config:
        orm_mode = True
