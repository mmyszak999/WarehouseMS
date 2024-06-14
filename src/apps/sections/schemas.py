from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator



class SectionBaseSchema(BaseModel):
    section_name: str = Field(max_length=400)
    max_weight: Decimal
    max_racks: int
    
    class Config:
        orm_mode = True


class SectionInputSchema(SectionBaseSchema):
    pass


class SectionUpdateSchema(BaseModel):
    section_name: Optional[str]
    max_weight: Optional[Decimal]
    max_racks: Optional[int]


class SectionBaseOutputSchema(SectionBaseSchema):
    available_weight: Decimal
    available_racks: int

    class Config:
        orm_mode = True
        

class SectionOutputSchema(SectionBaseOutputSchema):
    pass

    class Config:
        orm_mode = True