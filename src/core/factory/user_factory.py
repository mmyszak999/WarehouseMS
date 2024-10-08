from datetime import date
from decimal import Decimal
from typing import Optional

from src.apps.users.schemas import UserInputSchema, UserPasswordSchema, UserUpdateSchema
from src.core.factory.core import SchemaFactory
from src.core.utils.time import set_employment_date_for_factory


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
        can_move_stocks: bool = None,
        can_recept_stocks: bool = None,
        can_issue_stocks: bool = None,
    ):
        return self.schema_class(
            first_name=first_name or self.faker.first_name(),
            last_name=last_name or self.faker.last_name(),
            employment_date=employment_date or set_employment_date_for_factory(),
            email=email or self.faker.ascii_email(),
            birth_date=birth_date or self.faker.date_of_birth(),
            is_staff=is_staff or False,
            can_move_stocks=can_move_stocks or False,
            can_recept_stocks=can_recept_stocks or False,
            can_issue_stocks=can_issue_stocks or False,
        )


class UserPasswordSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=UserPasswordSchema):
        super().__init__(schema_class)

    def generate(self, password: str = "password", password_repeat: str = "password"):
        return self.schema_class(password=password, password_repeat=password_repeat)


class UserUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=UserUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        employment_date: Optional[date] = None,
        birth_date: Optional[date] = None,
        is_staff: Optional[bool] = None,
        can_move_stocks: Optional[bool] = None,
        can_recept_stocks: Optional[bool] = None,
        can_issue_stocks: Optional[bool] = None,
    ):
        return self.schema_class(
            first_name=first_name,
            last_name=last_name,
            employment_date=employment_date,
            birth_date=birth_date,
            is_staff=is_staff,
            can_move_stocks=can_move_stocks,
            can_recept_stocks=can_recept_stocks,
            can_issue_stocks=can_issue_stocks,
        )
