from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.category_schemas import (
    CategoryOutputSchema,
    CategoryIdListSchema
)


class ProductBaseSchema(BaseModel):
    name: str = Field(max_length=75)
    description: str
    weight: Decimal


class ProductInputSchema(ProductBaseSchema):
    wholesale_price: Decimal
    category_ids: CategoryIdListSchema
    amount_in_goods: int = 0


class ProductUpdateSchema(BaseModel):
    name: Optional[str]
    wholesale_price: Optional[Decimal]
    description: Optional[str]
    category_ids: Optional[CategoryIdListSchema]


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