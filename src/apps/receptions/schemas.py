from typing import Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.apps.products.schemas.product_schemas import ProductIdListSchema
from src.apps.stocks.schemas import StockBasicOutputSchema
from src.apps.users.schemas import UserInfoOutputSchema



class ReceptionProductInputSchema(BaseModel):
    product_id: str
    product_amount: int
    
    
class ReceptionInputSchema(BaseModel):
    products_data: list[ReceptionProductInputSchema]


class ReceptionBasicOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    reception_date: datetime
    
    class Config:
        orm_mode = True


class ReceptionOutputSchema(ReceptionBasicOutputSchema):
    stocks: list[StockBasicOutputSchema]

    class Config:
        orm_mode = True