from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.stocks.schemas import StockInputSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_product_weight, set_product_count


class StockInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=StockInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        product_weight: Decimal = None,
        weight: Decimal = None,
        product_count: int = None,
        product_id: str = None,
        reception_id: str = None
    ):
        if not product_count:
            product_count = set_product_count()
        return self.schema_class(
            product_count=product_count,
            weight=product_weight*product_count,
            product_id=product_id,
            reception_id=reception_id
        )
