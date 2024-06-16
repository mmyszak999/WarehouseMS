from contextlib import nullcontext as does_not_raise

import pytest
from pydantic.error_wrappers import ValidationError

from src.core.factory.section_factory import (
    SectionInputSchemaFactory,
    SectionUpdateSchemaFactory,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "section_param_value, result, schema",
    [
        # input schema part
        (
            4,
            does_not_raise(),
            SectionInputSchemaFactory(),
        ),
        (
            -1,
            pytest.raises(ValidationError),
            SectionInputSchemaFactory(),
        ),
        # update schema part
        (
            4,
            does_not_raise(),
            SectionUpdateSchemaFactory(),
        ),
        (
            0,
            pytest.raises(ValidationError),
            SectionUpdateSchemaFactory(),
        ),
    ],
)
async def test_section_input_schema_and_update_schema_raises_validation_error_when_params_are_not_positive(
    section_param_value, result, schema
):
    with result:
        schema.generate(
            max_racks=section_param_value,
        )
