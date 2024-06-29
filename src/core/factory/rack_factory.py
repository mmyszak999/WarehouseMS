from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.racks.schemas import RackInputSchema, RackUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_rack_levels, set_rack_weight


class RackInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=RackInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        section_id: str,
        rack_name: str = None,
        max_weight: Decimal = None,
        max_levels: int = None,
    ) -> RackInputSchema:
        return self.schema_class(
            section_id=section_id,
            rack_name=rack_name or self.faker.ecommerce_name(),
            max_weight=max_weight or set_rack_weight(),
            max_levels=max_levels or set_rack_levels(),
        )


class RackUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=RackUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        rack_name: Optional[str] = None,
        max_weight: Optional[Decimal] = None,
        max_levels: Optional[int] = None,
    ) -> RackUpdateSchema:
        return self.schema_class(
            rack_name=rack_name,
            max_weight=max_weight,
            max_levels=max_levels,
        )
