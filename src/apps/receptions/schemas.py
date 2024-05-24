from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from src.apps.products.schemas.product_schemas import ProductIdListSchema
from src.apps.users.schemas import UserInfoOutputSchema


class ReceptionInputSchema(BaseModel):
    product_ids: ProductIdListSchema


class ReceptionOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    reception_date: datetime

    class Config:
        orm_mode = True