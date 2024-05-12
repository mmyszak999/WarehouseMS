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


class UserInputSchema(UserBaseSchema):
    email: EmailStr = Field()
    birth_date: datetime.date
    is_staff: bool
    can_move_goods: bool
    can_recept_goods: bool
    can_issue_goods: bool
    
    @validator("birth_date")
    def validate_birth_date(cls, birth_date: datetime.date) -> datetime.date:
        if birth_date >= datetime.date.today():
            raise ValueError("Birth date must be in the past")
        return birth_date
    
    """@validator("employment_date")
    def validate_employment_date(cls, employment_date: datetime.date, values: dict[str, Any]) -> datetime.date:
        if employment_date <= values["birth_date"]:
            raise ValueError("Employment date can't be earlier than birth date")
        return employment_date"""


class UserPasswordSchema(BaseModel):
    password: str = Field(min_length=8, max_length=40)
    password_repeat: str = Field(min_length=8, max_length=40)

    @validator("password_repeat")
    def validate_passwords(cls, rep_password: str, values: dict[str, Any]) -> str:
        if rep_password != values["password"]:
            raise ValueError("Passwords are not identical")
        return rep_password


class UserInfoOutputSchema(UserBaseSchema):
    is_active: bool

    class Config:
        orm_mode = True


class UserOutputSchema(UserInputSchema):
    id: str
    is_active: bool
    is_superuser: bool
    is_staff: bool
    
    class Config:
        orm_mode = True