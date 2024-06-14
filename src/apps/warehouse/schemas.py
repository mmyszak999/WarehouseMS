from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.sections.schemas import SectionBaseOutputSchema



class WarehouseBaseSchema(BaseModel):
    warehouse_name: str = Field(max_length=400)
    max_sections: int
    max_waiting_rooms: int


class WarehouseInputSchema(WarehouseBaseSchema):
    pass


class WarehouseUpdateSchema(BaseModel):
    warehouse_name: Optional[str]
    max_sections: Optional[int]
    max_waiting_rooms: Optional[int]


class WarehouseBaseOutputSchema(WarehouseBaseSchema):
    available_sections: int
    available_waiting_rooms: int

    class Config:
        orm_mode = True
        

class WarehouseOutputSchema(WarehouseBaseOutputSchema):
    sections: list[SectionBaseOutputSchema]

    class Config:
        orm_mode = True