from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.stocks.schemas.stock_schemas import StockWithoutRackLevelSlotOutputSchema


class RackLevelSlotBaseSchema(BaseModel):
    rack_level_slot_number: int
    description: Optional[str] = Field(max_length=200)

    @validator("rack_level_slot_number")
    def validate_rack_level_slot_number(cls, rack_level_slot_number: int) -> int:
        if rack_level_slot_number is not None and rack_level_slot_number <= 0:
            raise ValueError("Rack level slot number must be positive!")
        return rack_level_slot_number

    class Config:
        orm_mode = True


class RackLevelSlotInputSchema(RackLevelSlotBaseSchema):
    rack_level_id: str


class RackLevelSlotUpdateSchema(BaseModel):
    description: Optional[str]


class RackLevelSlotBaseOutputSchema(RackLevelSlotBaseSchema):
    id: str
    is_active: bool
    rack_level_id: str
    stock_id: Optional[str]

    class Config:
        orm_mode = True


class RackLevelSlotOutputSchema(RackLevelSlotBaseOutputSchema):
    stock: Optional[StockWithoutRackLevelSlotOutputSchema]

    class Config:
        orm_mode = True