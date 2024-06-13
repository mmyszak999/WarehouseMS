from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.waiting_rooms.schemas import (
    WaitingRoomInputSchema,
    WaitingRoomUpdateSchema,
)
from src.core.factory.core import SchemaFactory
from src.core.utils.faker import set_waiting_room_stocks, set_waiting_room_weight


class WaitingRoomInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=WaitingRoomInputSchema):
        super().__init__(schema_class)

    def generate(self, max_stocks: int = None, max_weight: Decimal = None, name: str=None):
        return self.schema_class(
            max_stocks=max_stocks or set_waiting_room_stocks(),
            max_weight=max_weight or set_waiting_room_weight(),
            name=name or self.faker.ecommerce_name()
        )


class WaitingRoomUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=WaitingRoomUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self, max_stocks: Optional[int] = None, max_weight: Optional[Decimal] = None,
        name: Optional[str]=None
    ):
        return self.schema_class(max_stocks=max_stocks, max_weight=max_weight, name=name)
