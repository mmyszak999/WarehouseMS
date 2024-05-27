from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from src.apps.stocks.schemas import StockBasicOutputSchema, StockIssueInputSchema
from src.apps.users.schemas import UserInfoOutputSchema
from src.apps.products.schemas.product_schemas import ProductBasicOutputSchema
from src.apps.receptions.schemas import ReceptionStockOutputSchema


class IssueInputSchema(BaseModel):
    stock_ids: list[StockIssueInputSchema]
    description: str = Field(max_length=400)


class IssueOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    issue_date: datetime
    stocks: list[StockBasicOutputSchema]

    class Config:
        orm_mode = True


class IssueUpdateSchema(BaseModel):
    description: Optional[str] = Field(max_length=400)


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