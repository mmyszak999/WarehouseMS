from contextlib import nullcontext as does_not_raise

import pytest
from pydantic.error_wrappers import ValidationError

from src.core.factory.rack_factory import (
    RackInputSchemaFactory,
    RackUpdateSchemaFactory,
)
from tests.test_sections.conftest import db_sections
from src.apps.sections.schemas import SectionOutputSchema
from src.core.pagination.schemas import PagedResponseSchema



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rack_param_value, result, schema",
    [
        (
            4,
            does_not_raise(),
            RackInputSchemaFactory(),
        ),
        (
            -1,
            pytest.raises(ValidationError),
            RackInputSchemaFactory(),
        )
    ],
)
async def test_rack_input_schema_raises_validation_error_when_params_are_not_positive(
    rack_param_value, result, schema,
    db_sections: PagedResponseSchema[SectionOutputSchema]
):
    with result:
        schema.generate(
            section_id=db_sections.results[0].id,
            max_weight=rack_param_value,
        )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rack_param_value, result, schema",
    [
        (
            4,
            does_not_raise(),
            RackUpdateSchemaFactory(),
        ),
        (
            0,
            pytest.raises(ValidationError),
            RackUpdateSchemaFactory(),
        ),
    ],
)
async def test_rack_update_schema_raises_validation_error_when_params_are_not_positive(
    rack_param_value, result, schema,
):
    with result:
        schema.generate(
            max_weight=rack_param_value,
        )

