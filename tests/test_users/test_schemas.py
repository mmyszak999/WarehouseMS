from contextlib import nullcontext as does_not_raise
from datetime import datetime, timedelta

import pytest
from pydantic.error_wrappers import ValidationError

from src.apps.users.schemas import UserPasswordSchema
from src.core.factories import UserInputSchemaFactory, UserUpdateSchemaFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "employment_date, result",
    [
        (datetime.now() - timedelta(days=1), does_not_raise()),
        (datetime.now() + timedelta(days=1), pytest.raises(ValidationError)),
    ],
)
async def test_user_input_schema_raises_validation_error_when_employment_date_is_from_future(
    employment_date, result
):
    with result:
        UserInputSchemaFactory().generate(
            employment_date=employment_date,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "birth_date, result, schema",
    [
        #input schema part
        (datetime.now() - timedelta(days=1), does_not_raise(), UserInputSchemaFactory()),
        (datetime.now() + timedelta(days=1), pytest.raises(ValidationError), UserInputSchemaFactory()),
        
        #update schema part
        (datetime.now() - timedelta(days=1), does_not_raise(), UserUpdateSchemaFactory()),
        (datetime.now() + timedelta(days=1), pytest.raises(ValidationError), UserUpdateSchemaFactory()),
    ],
)
async def test_user_input_schema_and_update_schema_raises_validation_error_when_birth_date_is_from_future(
    birth_date, result, schema
):
    with result:
        schema.generate(
            birth_date=birth_date,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "password1, password2, result",
    [
        ("testtest1", "testtest1", does_not_raise()),
        ("testtest1", "testtest2", pytest.raises(ValidationError)),
    ],
)
async def test_user_password_schema_raises_validation_error_when_passwords_are_not_identical(
    password1, password2, result
):
    with result:
        UserPasswordSchema(
            password=password1,
            password_repeat=password2
        )