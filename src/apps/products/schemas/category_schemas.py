from typing import Optional

from pydantic import BaseModel, Field


class CategoryBaseSchema(BaseModel):
    name: str = Field(max_length=75)


class CategoryInputSchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(max_length=75)


class CategoryOutputSchema(CategoryBaseSchema):
    id: str

    class Config:
        orm_mode = True


class CategoryIdListSchema(BaseModel):
    id: list[str]