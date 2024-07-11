import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryBaseSchema(BaseModel):
    name: str = Field(max_length=75)

    class Config:
        orm_mode = True


class CategoryInputSchema(CategoryBaseSchema):
    pass

    class Config:
        orm_mode = True


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(max_length=75)

    class Config:
        orm_mode = True


class CategoryOutputSchema(CategoryBaseSchema):
    id: str
    created_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class CategoryIdListSchema(BaseModel):
    id: list[str]

    class Config:
        orm_mode = True
