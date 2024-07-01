from contextlib import nullcontext as does_not_raise

import pytest
from pydantic.error_wrappers import ValidationError

from src.apps.racks.schemas import RackOutputSchema
from src.core.factory.rack_level_factory import (
    RackLevelInputSchemaFactory,
    RackLevelUpdateSchemaFactory,
)
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_racks.conftest import db_racks
from tests.test_sections.conftest import db_sections
from tests.test_warehouse.conftest import db_warehouse


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rack_level_param_value, result, schema",
    [
        (
            4,
            does_not_raise(),
            RackLevelInputSchemaFactory(),
        ),
        (
            -1,
            pytest.raises(ValidationError),
            RackLevelInputSchemaFactory(),
        ),
    ],
)
async def test_rack_level_input_schema_raises_validation_error_when_params_are_not_positive(
    rack_level_param_value,
    result,
    schema,
    db_racks: PagedResponseSchema[RackOutputSchema],
):
    with result:
        schema.generate(
            rack_id=db_racks.results[0].id,
            rack_level_number=db_racks.results[0].max_levels,
            max_weight=rack_level_param_value,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rack_level_param_value, result, schema",
    [
        (
            4,
            does_not_raise(),
            RackLevelUpdateSchemaFactory(),
        ),
        (
            0,
            pytest.raises(ValidationError),
            RackLevelUpdateSchemaFactory(),
        ),
    ],
)
async def test_rack_level_update_schema_raises_validation_error_when_params_are_not_positive(
    rack_level_param_value,
    result,
    schema,
):
    with result:
        schema.generate(
            max_weight=rack_level_param_value,
        )
