from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.rack_levels.schemas import RackLevelBaseOutputSchema


class RackBaseSchema(BaseModel):
    rack_name: str = Field(max_length=400)
    max_weight: Decimal
    max_levels: int

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: Decimal) -> Decimal:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max rack weight must be positive!")
        return max_weight

    @validator("max_levels")
    def validate_max_levels(cls, max_levels: int) -> int:
        if max_levels is not None and max_levels <= 0:
            raise ValueError("Max rack levels must be positive!")
        return max_levels

    class Config:
        orm_mode = True


class RackInputSchema(RackBaseSchema):
    section_id: str


class RackUpdateSchema(BaseModel):
    rack_name: Optional[str]
    max_weight: Optional[Decimal]
    max_levels: Optional[int]

    @validator("max_weight")
    def validate_max_weight(cls, max_weight: Optional[Decimal]) -> Optional[Decimal]:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max rack weight must be positive!")
        return max_weight

    @validator("max_levels")
    def validate_max_levels(cls, max_levels: Optional[int]) -> Optional[int]:
        if max_levels is not None and max_levels <= 0:
            raise ValueError("Max rack levels must be positive!")
        return max_levels


class RackBaseOutputSchema(RackBaseSchema):
    id: str
    available_weight: Decimal
    occupied_weight: Decimal
    available_levels: int
    occupied_levels: int
    reserved_weight: Decimal
    weight_to_reserve: Decimal
    created_at: Optional[date]
    section_id: str

    class Config:
        orm_mode = True


class RackOutputSchema(RackBaseOutputSchema):
    rack_levels: list[RackLevelBaseOutputSchema]

    class Config:
        orm_mode = True
