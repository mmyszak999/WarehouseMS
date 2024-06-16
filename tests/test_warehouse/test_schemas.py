from contextlib import nullcontext as does_not_raise

import pytest
from pydantic.error_wrappers import ValidationError

from src.core.factory.warehouse_factory import (
    WarehouseInputSchemaFactory,
    WarehouseUpdateSchemaFactory,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "warehouse_param_value, result, schema",
    [
        # input schema part
        (
            4,
            does_not_raise(),
            WarehouseInputSchemaFactory(),
        ),
        (
            -1,
            pytest.raises(ValidationError),
            WarehouseInputSchemaFactory(),
        ),
        # update schema part
        (
            4,
            does_not_raise(),
            WarehouseUpdateSchemaFactory(),
        ),
        (
            0,
            pytest.raises(ValidationError),
            WarehouseUpdateSchemaFactory(),
        ),
    ],
)
async def test_warehouse_input_schema_and_update_schema_raises_validation_error_when_params_are_not_positive(
    warehouse_param_value, result, schema
):
    with result:
        schema.generate(
            max_sections=warehouse_param_value,
        )
