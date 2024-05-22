from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.products.schemas.category_schemas import CategoryInputSchema, CategoryUpdateSchema
from src.core.factory.core import SchemaFactory


class CategoryInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=CategoryInputSchema):
        super().__init__(schema_class)

    def generate(self, name: str = None):
        return self.schema_class(
            name=name or self.faker.ecommerce_category(),
        )


class CategoryUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=CategoryUpdateSchema):
        super().__init__(schema_class)

    def generate(self, name: Optional[str] = None):
        return self.schema_class(name=name)