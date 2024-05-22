from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.products.schemas.category_schemas import CategoryIdListSchema
from src.apps.products.schemas.product_schemas import ProductUpdateSchema, ProductInputSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_product_weight


class ProductInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ProductInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        category_ids: CategoryIdListSchema = CategoryIdListSchema(id=[]),
        name: str = None,
        wholesale_price: Decimal = None,
        description: str = None,
        weight: Decimal = None
    ):
        return self.schema_class(
            category_ids=category_ids,
            name=name or self.faker.ecommerce_name(),
            wholesale_price=wholesale_price or Decimal(self.faker.ecommerce_price()),
            description=description or self.faker.sentence(),
            weight=weight or set_product_weight()
        )


class ProductUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ProductUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        category_ids: Optional[CategoryIdListSchema] = None,
        name: Optional[str] = None,
        wholesale_price: Optional[Decimal] = None,
        description: Optional[str] = None
    ):
        return self.schema_class(
            category_ids=category_ids,
            name=name,
            wholesale_price=wholesale_price,
            description=description,
        )
