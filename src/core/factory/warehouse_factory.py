from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.warehouse.schemas import WarehouseInputSchema, WarehouseUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_max_sections, set_max_waiting_rooms


class WarehouseInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=WarehouseInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        warehouse_name: str = None,
        max_sections: int = None,
        max_waiting_rooms: int = None,
    ):
        return self.schema_class(
            warehouse_name=warehouse_name or self.faker.ecommerce_name(),
            max_sections=max_sections or set_max_sections(),
            max_waiting_rooms=max_waiting_rooms or set_max_waiting_rooms(),
        )


class WarehouseUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=WarehouseUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        warehouse_name: Optional[str] = None,
        max_sections: Optional[int] = None,
        max_waiting_rooms: Optional[int] = None,
    ):
        return self.schema_class(
            warehouse_name=warehouse_name,
            max_sections=max_sections,
            max_waiting_rooms=max_waiting_rooms,
        )
