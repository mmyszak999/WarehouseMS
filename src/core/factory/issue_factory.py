from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.stocks.schemas import StockIssueInputSchema
from src.apps.issues.schemas import IssueInputSchema, IssueUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_product_weight, set_product_count


class IssueInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=IssueInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        stock_ids: list[StockIssueInputSchema],
        desctiption: Optional[str] = None
    ):
        return self.schema_class(
            products_data=stock_ids,
            desctiption=desctiption or self.faker.sentence()
        )


class IssueUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=IssueUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        desctiption: Optional[str] = None
    ):
        return self.schema_class(
            desctiption=desctiption
        )