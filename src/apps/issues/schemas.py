from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionStockOutputSchema
from src.apps.stocks.schemas import StockBasicOutputSchema, StockIssueInputSchema
from src.apps.users.schemas import UserInfoOutputSchema


class IssueInputSchema(BaseModel):
    stock_ids: list[StockIssueInputSchema]
    description: Optional[str] = Field(max_length=400)

    class Config:
        orm_mode = True


class IssueUpdateSchema(BaseModel):
    description: Optional[str] = Field(max_length=400)

    class Config:
        orm_mode = True


class IssueBasicOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    issue_date: datetime
    description: Optional[str]

    class Config:
        orm_mode = True


class IssueStockOutputSchema(ReceptionStockOutputSchema):
    pass

    class Config:
        orm_mode = True


class IssueOutputSchema(IssueBasicOutputSchema):
    stocks: list[IssueStockOutputSchema]

    class Config:
        orm_mode = True
