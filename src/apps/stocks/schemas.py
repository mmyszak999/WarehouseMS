from typing import Optional

from pydantic import BaseModel, Field


class StockInputSchema(BaseModel):
    pass


class StockBasicOutputSchema(BaseModel):
    pass


class StockOutputSchema(BaseModel):
    pass

    class Config:
        orm_mode = True


class StockIdListSchema(BaseModel):
    id: list[str]
