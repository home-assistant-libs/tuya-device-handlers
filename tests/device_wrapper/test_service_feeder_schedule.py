"""Test DeviceWrapper feeder schedule functionality"""

from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion

from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    Base64Encoder,
    get_meal_plan_serializer,
)

from .. import create_device


def decoded_meal_plan() -> list[dict[str, Any]]:
    """Return raw meal plan data for testing."""
    return [
        {
            "days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "hour": 9,
            "minute": 0,
            "portion": 1,
            "enabled": 1,
        },
        {
            "days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "hour": 9,
            "minute": 30,
            "portion": 1,
            "enabled": 1,
        },
        {
            "days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "hour": 12,
            "minute": 0,
            "portion": 1,
            "enabled": 1,
        },
        {
            "days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "hour": 15,
            "minute": 0,
            "portion": 2,
            "enabled": 1,
        },
        {
            "days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "hour": 21,
            "minute": 0,
            "portion": 2,
            "enabled": 1,
        },
    ]


def test_get_meal_plan_serializer() -> None:
    """Test get_meal_plan_serializer returns correct serializer."""
    device = create_device("cwwsq_wfkzyy0evslzsmoi.json")
    serializer = get_meal_plan_serializer(device)
    assert isinstance(serializer, Base64Encoder)


def test_get_meal_data(
    snapshot: SnapshotAssertion,
) -> None:
    """Test get_meal_data decodes meal plan correctly."""
    device = create_device("cwwsq_wfkzyy0evslzsmoi.json")

    serializer = get_meal_plan_serializer(device)
    assert serializer is not None

    result = serializer.get_meal_data(device)
    assert result == snapshot


def test_get_meal_plan_update_commands() -> None:
    """Test get_meal_plan_update_commands encodes data correctly."""
    device = create_device("cwwsq_wfkzyy0evslzsmoi.json")

    serializer = get_meal_plan_serializer(device)
    assert serializer is not None

    commands = serializer.get_meal_plan_update_commands(
        device, decoded_meal_plan()
    )
    assert commands == [
        {"code": "meal_plan", "value": "fwkAAQF/CR4BAX8MAAEBfw8AAgF/FQACAQ=="}
    ]


def test_get_meal_data_invalid_data() -> None:
    """Test get_meal_data with invalid data."""
    device = create_device("cwwsq_wfkzyy0evslzsmoi.json")
    # No meal_plan in status
    device.status.pop("meal_plan", None)

    serializer = get_meal_plan_serializer(device)
    assert serializer is not None

    with pytest.raises(ValueError, match="Invalid Base64 meal plan data"):
        serializer.get_meal_data(device)

    # Invalid meal_plan value
    device.status["meal_plan"] = "unknown"

    with pytest.raises(ValueError, match="Invalid Base64 meal plan data"):
        serializer.get_meal_data(device)


def test_get_meal_plan_update_commands_no_function() -> None:
    """Test get_meal_plan_update_commands when meal_plan function not supported."""
    device = create_device("cwwsq_wfkzyy0evslzsmoi.json")
    # Remove meal_plan from function
    device.function.pop("meal_plan", None)

    serializer = get_meal_plan_serializer(device)
    assert serializer is not None

    with pytest.raises(
        ValueError,
        match=(
            "Feeder with ID iomszlsve0yyzkfw "
            "does not support meal plan functionality"
        ),
    ):
        serializer.get_meal_plan_update_commands(device, decoded_meal_plan())
