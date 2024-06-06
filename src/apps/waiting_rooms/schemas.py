from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionStockOutputSchema
from src.apps.stocks.schemas import StockWithoutWaitingRoomOutputSchema, StockIssueInputSchema
from src.apps.users.schemas import UserInfoOutputSchema


class WaitingRoomBaseSchema(BaseModel):
    max_stocks: int
    max_weight: Decimal

    @validator("max_stocks")
    def validate_max_stocks(cls, max_stocks: int) -> int:
        if max_stocks is not None and max_stocks <= 0:
            raise ValueError("Max stocks must be positive!")
        return max_stocks

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: Decimal) -> Decimal:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max weight must be positive!")
        return max_weight

    class Config:
        orm_mode = True


class WaitingRoomInputSchema(WaitingRoomBaseSchema):
    pass

    class Config:
        orm_mode = True


class WaitingRoomUpdateSchema(BaseModel):
    max_stocks: Optional[int]
    max_weight: Optional[Decimal]

    @validator("max_stocks")
    def validate_max_stocks(cls, max_stocks: Optional[int]) -> Optional[int]:
        if max_stocks is not None and max_stocks <= 0:
            raise ValueError("Max stocks must be positive!")
        return max_stocks

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: Optional[Decimal]) -> Optional[Decimal]:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max weight must be positive!")
        return max_weight
    
    class Config:
        orm_mode = True


class WaitingRoomBasicOutputSchema(WaitingRoomBaseSchema):
    id: str
    stocks: list[StockWithoutWaitingRoomOutputSchema]
    occupied_slots: int
    current_stock_weight: Decimal
    available_slots: int
    available_stock_weight: Decimal

    class Config:
        orm_mode = True


class WaitingRoomOutputSchema(WaitingRoomBasicOutputSchema):
    available_slots: int
    available_stock_weight: Decimal

    class Config:
        orm_mode = True
