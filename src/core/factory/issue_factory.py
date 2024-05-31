from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.issues.schemas import IssueInputSchema, IssueUpdateSchema
from src.apps.stocks.schemas import StockIssueInputSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_product_count, set_product_weight


class IssueInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=IssueInputSchema):
        super().__init__(schema_class)

    def generate(
        self, stock_ids: list[StockIssueInputSchema], description: Optional[str] = None
    ):
        return self.schema_class(
            stock_ids=stock_ids, description=description or self.faker.sentence()
        )


class IssueUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=IssueUpdateSchema):
        super().__init__(schema_class)

    def generate(self, desctiption: Optional[str] = None):
        return self.schema_class(desctiption=desctiption)
