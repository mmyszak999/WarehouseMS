from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.rack_level_slots.schemas import (
    RackLevelSlotInputSchema,
    RackLevelSlotUpdateSchema,
)
from src.core.factory.core import SchemaFactory


class RackLevelSlotInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=RackLevelSlotInputSchema):
        super().__init__(schema_class)

    def generate(
        self, rack_level_slot_number: int, rack_level_id: str, description: str = None
    ) -> RackLevelSlotInputSchema:
        return self.schema_class(
            rack_level_slot_number=rack_level_slot_number,
            rack_level_id=rack_level_id,
            description=description or self.faker.ecommerce_name(),
        )


class RackLevelSlotUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=RackLevelSlotUpdateSchema):
        super().__init__(schema_class)

    def generate(self, description: str = None) -> RackLevelSlotUpdateSchema:
        return self.schema_class(description=description)
