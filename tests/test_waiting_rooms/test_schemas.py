from contextlib import nullcontext as does_not_raise
from datetime import datetime, timedelta

import pytest
from pydantic.error_wrappers import ValidationError

from src.core.factory.waiting_room_factory import (
    WaitingRoomInputSchemaFactory,
    WaitingRoomUpdateSchemaFactory,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "waiting_room_param_value, result, schema",
    [
        # input schema part
        (
            4,
            does_not_raise(),
            WaitingRoomInputSchemaFactory(),
        ),
        (
            -1,
            pytest.raises(ValidationError),
            WaitingRoomInputSchemaFactory(),
        ),
        # update schema part
        (
            4,
            does_not_raise(),
            WaitingRoomUpdateSchemaFactory(),
        ),
        (
            0,
            pytest.raises(ValidationError),
            WaitingRoomUpdateSchemaFactory(),
        ),
    ],
)
async def test_waiting_room_input_schema_and_update_schema_raises_validation_error_when_params_are_incorrect(
    waiting_room_param_value, result, schema
):
    with result:
        schema.generate(
            max_stocks=waiting_room_param_value,
            max_weight=waiting_room_param_value,
        )
