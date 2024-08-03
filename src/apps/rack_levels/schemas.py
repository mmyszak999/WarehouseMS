from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.rack_level_slots.schemas import RackLevelSlotBaseOutputSchema


class RackLevelBaseSchema(BaseModel):
    rack_level_number: int
    description: Optional[str] = Field(max_length=400)
    max_weight: Decimal
    max_slots: int

    @validator("rack_level_number")
    def validate_rack_level_number(cls, rack_level_number: int) -> int:
        if rack_level_number is not None and rack_level_number <= 0:
            raise ValueError("Rack level number must be positive!")
        return rack_level_number

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: Decimal) -> Decimal:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max rack level weight must be positive!")
        return max_weight

    @validator("max_slots")
    def validate_max_slots(cls, max_slots: int) -> int:
        if max_slots is not None and max_slots <= 0:
            raise ValueError("Max rack level slots must be positive!")
        return max_slots

    class Config:
        orm_mode = True


class RackLevelInputSchema(RackLevelBaseSchema):
    rack_id: str


class RackLevelUpdateSchema(BaseModel):
    description: Optional[str]
    max_weight: Optional[Decimal]
    max_slots: Optional[int]

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: Optional[Decimal]) -> Optional[Decimal]:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max rack level weight must be positive!")
        return max_weight

    @validator("max_slots")
    def validate_max_slots(cls, max_slots: Optional[int]) -> Optional[int]:
        if max_slots is not None and max_slots <= 0:
            raise ValueError("Max rack level slots must be positive!")
        return max_slots


class RackLevelBaseOutputSchema(RackLevelBaseSchema):
    id: str
    available_weight: Decimal
    occupied_weight: Decimal
    available_slots: int
    occupied_slots: int
    active_slots: int
    inactive_slots: int
    created_at: Optional[date]
    rack_id: str

    class Config:
        orm_mode = True


class RackLevelOutputSchema(RackLevelBaseOutputSchema):
    rack_level_slots: list[RackLevelSlotBaseOutputSchema]

    class Config:
        orm_mode = True
