from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.product_schemas import (
    ProductBasicOutputSchema,
    ProductIdListSchema,
)
from src.apps.users.schemas import UserInfoOutputSchema


class ReceptionProductInputSchema(BaseModel):
    product_id: str
    product_count: int
    waiting_room_id: str = None
    rack_level_slot_id: str = None
    rack_level_id: str = None

    @validator("product_count")
    def validate_product_count(cls, product_count: int) -> int:
        if product_count <= 0:
            raise ValueError("Product count must be positive!")
        return product_count

    class Config:
        orm_mode = True


class ReceptionInputSchema(BaseModel):
    products_data: list[ReceptionProductInputSchema]
    description: Optional[str] = Field(max_length=400)

    class Config:
        orm_mode = True


class ReceptionUpdateSchema(BaseModel):
    description: Optional[str] = Field(max_length=400)

    class Config:
        orm_mode = True


class ReceptionBasicOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    reception_date: datetime
    description: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class ReceptionStockOutputSchema(BaseModel):
    id: str
    weight: Decimal
    product_count: int
    product: ProductBasicOutputSchema

    class Config:
        orm_mode = True


class ReceptionOutputSchema(ReceptionBasicOutputSchema):
    stocks: list[ReceptionStockOutputSchema]

    class Config:
        orm_mode = True
