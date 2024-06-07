from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionBasicOutputSchema
from src.apps.users.schemas import UserInfoOutputSchema


class StockBaseSchema(BaseModel):
    weight: Decimal
    product_count: int

    @validator("weight")
    def validate_weight(cls, weight: int) -> int:
        if weight and (weight < 0):
            raise ValueError("Stock weight must be positive! ")
        return weight

    @validator("product_count")
    def validate_product_count(cls, product_count: int) -> int:
        if product_count and (product_count < 0):
            raise ValueError("Product count must be positive! ")
        return product_count

    class Config:
        orm_mode = True


class StockInputSchema(StockBaseSchema):
    product_id: str
    reception_id: Optional[str]
    waiting_room_id: Optional[str]

    class Config:
        orm_mode = True


class StockWaitingRoomBasicOutputSchema(BaseModel):
    max_stocks: int
    max_weight: Decimal
    id: str

    class Config:
        orm_mode = True


class StockWithoutWaitingRoomOutputSchema(StockBaseSchema):
    id: str
    product: ProductBasicOutputSchema
    reception: ReceptionBasicOutputSchema

    class Config:
        orm_mode = True


class StockUserInfoOutputSchema(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=75)
    employment_date: date
    is_active: bool

    class Config:
        orm_mode = True


class StockBasicOutputSchema(StockWithoutWaitingRoomOutputSchema):
    waiting_room: Optional[StockWaitingRoomBasicOutputSchema]
    users: Optional[StockUserInfoOutputSchema]

    class Config:
        orm_mode = True


class StockOutputSchema(StockBasicOutputSchema):
    is_issued: bool
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class StockIssueInputSchema(BaseModel):
    id: str

    class Config:
        orm_mode = True


class StockWaitingRoomInputSchema(StockIssueInputSchema):
    pass

    class Config:
        orm_mode = True
