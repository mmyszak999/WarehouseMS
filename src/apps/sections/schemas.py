from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator



class SectionBaseSchema(BaseModel):
    section_name: str = Field(max_length=400)
    max_weight: Decimal
    max_racks: int
    
    @validator("max_weight")
    def validate_max_weight(cls, max_weight: int) -> int:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max section weight must be positive!")
        return max_weight

    @validator("max_racks")
    def validate_max_racks(cls, max_racks: Decimal) -> Decimal:
        if max_racks is not None and max_racks <= 0:
            raise ValueError("Max section racks must be positive!")
        return max_racks
    
    class Config:
        orm_mode = True


class SectionInputSchema(SectionBaseSchema):
    pass


class SectionUpdateSchema(BaseModel):
    section_name: Optional[str]
    max_weight: Optional[Decimal]
    max_racks: Optional[int]
    
    @validator("max_weight")
    def validate_max_weight(cls, max_weight: Optional[int]) -> Optional[int]:
        if max_weight is not None and max_weight <= 0:
            raise ValueError("Max section weight must be positive!")
        return max_weight

    @validator("max_racks")
    def validate_max_racks(cls, max_racks: Optional[Decimal]) -> Optional[Decimal]:
        if max_racks is not None and max_racks <= 0:
            raise ValueError("Max section racks must be positive!")
        return max_racks


class SectionBaseOutputSchema(SectionBaseSchema):
    available_weight: Decimal
    available_racks: int

    class Config:
        orm_mode = True
        

class SectionOutputSchema(SectionBaseOutputSchema):
    pass

    class Config:
        orm_mode = True