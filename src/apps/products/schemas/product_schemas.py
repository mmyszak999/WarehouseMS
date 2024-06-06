from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.category_schemas import (
    CategoryIdListSchema,
    CategoryOutputSchema,
)


class ProductBaseSchema(BaseModel):
    name: str = Field(max_length=75)
    description: str
    weight: Decimal
    
    class Config:
        orm_mode = True


class ProductInputSchema(ProductBaseSchema):
    wholesale_price: Decimal
    category_ids: CategoryIdListSchema
    
    class Config:
        orm_mode = True


class ProductUpdateSchema(BaseModel):
    name: Optional[str]
    wholesale_price: Optional[Decimal]
    description: Optional[str]
    category_ids: Optional[CategoryIdListSchema]
    
    class Config:
        orm_mode = True


class ProductBasicOutputSchema(ProductBaseSchema):
    id: str
    categories: list[CategoryOutputSchema]

    class Config:
        orm_mode = True


class ProductOutputSchema(ProductBasicOutputSchema):
    wholesale_price: Decimal
    amount_in_goods: int
    legacy_product: bool

    class Config:
        orm_mode = True


class RemovedProductOutputSchema(ProductBaseSchema):
    legacy_product: bool

    class Config:
        orm_mode = True


class ProductIdListSchema(BaseModel):
    id: list[str]
    
    class Config:
        orm_mode = True
