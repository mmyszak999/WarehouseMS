from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionStockOutputSchema
from src.apps.users.schemas import UserInfoOutputSchema


class StockIssueInputSchema(BaseModel):
    id: str

    class Config:
        orm_mode = True


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
    created_at: Optional[date]

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
