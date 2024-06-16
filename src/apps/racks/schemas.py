from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator


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
    pass


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

    class Config:
        orm_mode = True


class RackOutputSchema(RackBaseOutputSchema):
    pass

    class Config:
        orm_mode = True
