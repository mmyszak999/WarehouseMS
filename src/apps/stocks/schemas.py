from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field

from src.apps.receptions.schemas import ReceptionBasicOutputSchema
from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema


class StockBaseSchema(BaseModel):
    weight: Decimal
    product_count: int


class StockInputSchema(StockBaseSchema):
    product_id: str
    reception_id: str
    

class StockBasicOutputSchema(StockBaseSchema):
    product: ProductBasicOutputSchema
    reception: ReceptionBasicOutputSchema
    


class StockOutputSchema(StockBasicOutputSchema):
    is_issued: bool
    updated_at: bool

    class Config:
        orm_mode = True


class StockIdListSchema(BaseModel):
    id: list[str]
