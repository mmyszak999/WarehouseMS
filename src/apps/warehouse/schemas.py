from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.sections.schemas import SectionBaseOutputSchema


class WarehouseBaseSchema(BaseModel):
    warehouse_name: str = Field(max_length=400)
    max_sections: int
    max_waiting_rooms: int
    
    @validator("max_sections")
    def validate_max_sections(cls, max_sections: int) -> int:
        if max_sections is not None and max_sections <= 0:
            raise ValueError("Max sections must be positive!")
        return max_sections

    @validator("max_waiting_rooms")
    def validate_max_waiting_rooms(cls, max_waiting_rooms: Decimal) -> Decimal:
        if max_waiting_rooms is not None and max_waiting_rooms <= 0:
            raise ValueError("Max waiting rooms must be positive!")
        return max_waiting_rooms
    
    class Config:
        orm_mode = True


class WarehouseInputSchema(WarehouseBaseSchema):
    pass


class WarehouseUpdateSchema(BaseModel):
    warehouse_name: Optional[str]
    max_sections: Optional[int]
    max_waiting_rooms: Optional[int]
    
    @validator("max_sections")
    def validate_max_sections(cls, max_sections: Optional[int]) -> Optional[int]:
        if max_sections is not None and max_sections <= 0:
            raise ValueError("Max sections must be positive!")
        return max_sections

    @validator("max_waiting_rooms")
    def validate_max_waiting_rooms(cls, max_waiting_rooms: Optional[Decimal]) -> Optional[Decimal]:
        if max_waiting_rooms is not None and max_waiting_rooms <= 0:
            raise ValueError("Max waiting rooms must be positive!")
        return max_waiting_rooms


class WarehouseBaseOutputSchema(WarehouseBaseSchema):
    id: str
    available_sections: int
    available_waiting_rooms: int
    occupied_sections: int
    occupied_waiting_rooms: int

    class Config:
        orm_mode = True
        

class WarehouseOutputSchema(WarehouseBaseOutputSchema):
    sections: list[SectionBaseOutputSchema]

    class Config:
        orm_mode = True