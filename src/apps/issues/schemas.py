from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from src.apps.stocks.schemas import StockBasicOutputSchema, StockIdListSchema
from src.apps.users.schemas import UserInfoOutputSchema


class IssueInputSchema(BaseModel):
    stock_ids: StockIdListSchema


class IssueOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    issue_date: datetime
    stocks: list[StockBasicOutputSchema]

    class Config:
        orm_mode = True