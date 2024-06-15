from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.weight.schemas import (
    SectionInputSchema,
    SectionUpdateSchema
)
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_max_racks, set_max_section_weight


class SectionInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=SectionInputSchema):
        super().__init__(schema_class)

    def generate(
        self, section_name: str = None, max_weight: Decimal = None, max_racks: int = None
    ):
        return self.schema_class(
            section_name=section_name or self.faker.ecommerce_name(),
            max_weight=max_weight or set_max_section_weight(),
            max_racks=max_racks or set_max_racks(),
        )


class SectionUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=SectionUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        section_name: Optional[str] = None, max_weight: Optional[Decimal] = None, max_racks: Optional[int] = None
    ):
        return self.schema_class(
            section_name=section_name,
            max_weight=max_weight,
            max_racks=max_racks,
        )