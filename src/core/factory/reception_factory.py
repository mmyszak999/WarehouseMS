from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.stocks.schemas import StockInputSchema
from src.apps.receptions.schemas import ReceptionInputSchema, ReceptionProductInputSchema, ReceptionUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_product_weight, set_product_count


class ReceptionInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ReceptionInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        products_data: list[ReceptionProductInputSchema],
        desctiption: Optional[str] = None
    ):
        return self.schema_class(
            products_data=products_data,
            desctiption=desctiption or self.faker.sentence()
        )


class ReceptionUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ReceptionUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        desctiption: Optional[str] = None
    ):
        return self.schema_class(
            desctiption=desctiption
        )