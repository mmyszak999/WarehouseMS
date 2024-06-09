from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.receptions.schemas import (
    ReceptionInputSchema,
    ReceptionProductInputSchema,
    ReceptionUpdateSchema,
)
from src.apps.stocks.schemas.stock_schemas import StockInputSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_product_count, set_product_weight


class ReceptionInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ReceptionInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        products_data: list[ReceptionProductInputSchema] = None,
        description: Optional[str] = None,
    ):
        return self.schema_class(
            products_data=products_data,
            description=description or self.faker.sentence(),
        )


class ReceptionUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ReceptionUpdateSchema):
        super().__init__(schema_class)

    def generate(self, description: Optional[str] = None):
        return self.schema_class(description=description)


class ReceptionProductInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ReceptionProductInputSchema):
        super().__init__(schema_class)

    def generate(self, product_id: str, product_count: int = None):
        return self.schema_class(
            product_id=product_id, product_count=product_count or set_product_count()
        )
