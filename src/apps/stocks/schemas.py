from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionBasicOutputSchema


class StockBaseSchema(BaseModel):
    weight: Decimal
    product_count: int

    @validator("weight")
    def validate_weight(cls, weight: int) -> int:
        if weight and (weight < 0):
            raise ValueError("Stocks weight must be positive! ")
        return weight

    @validator("product_count")
    def validate_product_count(cls, product_count: int) -> int:
        if product_count and (product_count < 0):
            raise ValueError("Product_count must be positive! ")
        return product_count


class StockInputSchema(StockBaseSchema):
    product_id: str
    reception_id: Optional[str]
    waiting_room_id: Optional[str]


class StockWaitingRoomBasicOutputSchema(BaseModel):
    max_stocks: int
    max_weight: Decimal
    id: str

    class Config:
        orm_mode = True


class StockBasicOutputSchema(StockBaseSchema):
    id: str
    product: ProductBasicOutputSchema
    reception: ReceptionBasicOutputSchema
    waiting_room: Optional[StockWaitingRoomBasicOutputSchema]

    class Config:
        orm_mode = True


class StockOutputSchema(StockBasicOutputSchema):
    is_issued: bool
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class StockIssueInputSchema(BaseModel):
    id: str


class StockWaitingRoomInputSchema(StockIssueInputSchema):
    pass
