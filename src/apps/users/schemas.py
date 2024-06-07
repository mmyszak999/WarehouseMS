import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserLoginInputSchema(BaseModel):
    email: EmailStr = Field()
    password: str = Field(min_length=8, max_length=40)


class UserBaseSchema(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=75)
    employment_date: datetime.date

    @validator("employment_date")
    def validate_employment_date(cls, employment_date: datetime.date) -> datetime.date:
        if employment_date >= datetime.date.today():
            raise ValueError("Employment date must be in the past")
        return employment_date

    class Config:
        orm_mode = True


class UserInputSchema(UserBaseSchema):
    email: EmailStr = Field()
    birth_date: datetime.date
    is_staff: bool
    can_move_stocks: bool
    can_recept_stocks: bool
    can_issue_stocks: bool

    @validator("birth_date")
    def validate_birth_date(cls, birth_date: datetime.date) -> datetime.date:
        if birth_date >= datetime.date.today():
            raise ValueError("Birth date must be in the past")
        return birth_date

    class Config:
        orm_mode = True


class UserPasswordSchema(BaseModel):
    password: str = Field(min_length=8, max_length=40)
    password_repeat: str = Field(min_length=8, max_length=40)

    @validator("password_repeat")
    def validate_passwords(cls, rep_password: str, values: dict[str, Any]) -> str:
        if rep_password != values["password"]:
            raise ValueError("Passwords are not identical")
        return rep_password

    class Config:
        orm_mode = True


class UserUpdateSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    employment_date: Optional[datetime.date]
    birth_date: Optional[datetime.date]
    can_move_stocks: Optional[bool]
    can_recept_stocks: Optional[bool]
    can_issue_stocks: Optional[bool]

    @validator("birth_date")
    def validate_birth_date(cls, birth_date: datetime.date) -> datetime.date:
        if birth_date and (birth_date >= datetime.date.today()):
            raise ValueError("Birth date must be in the past")
        return birth_date

    class Config:
        orm_mode = True


class UserInfoOutputSchema(UserBaseSchema):
    is_active: bool

    class Config:
        orm_mode = True


class UserOutputSchema(UserInputSchema):
    id: str
    is_active: bool
    is_superuser: bool
    is_staff: bool
    has_password_set: bool

    class Config:
        orm_mode = True
