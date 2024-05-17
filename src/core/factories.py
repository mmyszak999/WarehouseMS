from abc import abstractmethod
from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.users.schemas import UserInputSchema


class SchemaFactory:
    def __init__(self, schema_class):
        self.schema_class = schema_class
        self.faker = initialize_faker()

    @abstractmethod
    def generate(self, **kwargs):
        raise NotImplementedError()


class UserInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=UserInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        first_name: str = None,
        last_name: str = None,
        employment_date: date = None,
        email: str = None,
        birth_date: date = None,
        is_staff: bool = None,
        can_move_goods: bool = None,
        can_recept_goods: bool = None,
        can_issue_goods: bool = None
    ):
        return self.schema_class(
            first_name=first_name or self.faker.first_name(),
            last_name=last_name or self.faker.last_name(),
            mployment_date=employment_date or self.faker.date_of_birth(),
            email=email or self.faker.ascii_email(),
            birth_date=birth_date or self.faker.date_of_birth(),
            is_staff=is_staff,
            can_recept_goods=can_recept_goods,
            can_issue_goods=can_issue_goods
        )
