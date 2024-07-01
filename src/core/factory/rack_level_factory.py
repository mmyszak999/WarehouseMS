from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.rack_levels.schemas import RackLevelInputSchema, RackLevelUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_rack_level_slots, set_rack_level_weight


class RackLevelInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=RackLevelInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        rack_id: str,
        rack_level_number: int,
        description: str = None,
        max_weight: Decimal = None,
        max_slots: int = None,
    ) -> RackLevelInputSchema:
        return self.schema_class(
            rack_id=rack_id,
            rack_level_number=rack_level_number,
            description=description or self.faker.ecommerce_name(),
            max_weight=max_weight or set_rack_level_weight(),
            max_slots=max_slots or set_rack_level_slots(),
        )


class RackLevelUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=RackLevelUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        description: str = None,
        max_weight: Decimal = None,
        max_slots: int = None,
    ) -> RackLevelUpdateSchema:
        return self.schema_class(
            description=description,
            max_weight=max_weight,
            max_slots=max_slots,
        )