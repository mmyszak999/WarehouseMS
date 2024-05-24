from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from src.apps.products.schemas.product_schemas import ProductIdListSchema
from src.apps.users.schemas import UserInfoOutputSchema


class IssueInputSchema(BaseModel):
    stock_ids: ProductIdListSchema


class IssueOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    issue_date: datetime

    class Config:
        orm_mode = True