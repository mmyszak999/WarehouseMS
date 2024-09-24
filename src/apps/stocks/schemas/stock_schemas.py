from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.issues.schemas import IssueBasicOutputSchema
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
    rack_level_slot_id: Optional[str]

    class Config:
        orm_mode = True


class StockWaitingRoomBasicOutputSchema(BaseModel):
    max_stocks: int
    max_weight: Decimal
    name: Optional[str]
    id: str

    class Config:
        orm_mode = True


class StockRackLevelSlotBasicOutputSchema(BaseModel):
    rack_level_slot_number: int
    description: Optional[str]
    is_active: bool
    id: str

    class Config:
        orm_mode = True


class StockWithoutWaitingRoomOutputSchema(StockBaseSchema):
    id: str
    product: ProductBasicOutputSchema

    class Config:
        orm_mode = True


class StockWithoutRackLevelSlotOutputSchema(StockWithoutWaitingRoomOutputSchema):
    pass

    class Config:
        orm_mode = True


class StockBasicOutputSchema(StockWithoutWaitingRoomOutputSchema):
    waiting_room: Optional[StockWaitingRoomBasicOutputSchema]
    rack_level_slot: Optional[StockRackLevelSlotBasicOutputSchema]
    created_at: Optional[date]
    waiting_room_id: Optional[str]
    rack_level_slot_id: Optional[str]

    class Config:
        orm_mode = True


class StockOutputSchema(StockBasicOutputSchema):
    is_issued: bool
    updated_at: Optional[datetime]
    reception: Optional[ReceptionBasicOutputSchema]
    issue: Optional[IssueBasicOutputSchema]

    class Config:
        orm_mode = True


class StockWaitingRoomInputSchema(BaseModel):
    id: str

    class Config:
        orm_mode = True


class StockRackLevelInputSchema(StockWaitingRoomInputSchema):
    id: str

    class Config:
        orm_mode = True


class StockRackLevelSlotInputSchema(StockWaitingRoomInputSchema):
    pass

    class Config:
        orm_mode = True
