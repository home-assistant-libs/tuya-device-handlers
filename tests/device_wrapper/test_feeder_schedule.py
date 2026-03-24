"""Test DeviceWrapper feeder schedule functionality"""

from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.device_wrapper.feeder_schedule import (
    Base64Encoder,
    get_meal_plan_serializer,
)


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


def test_get_meal_plan_serializer(
    mock_device: CustomerDevice,
) -> None:
    """Test get_meal_plan_serializer returns correct serializer."""
    mock_device.product_id = "wfkzyy0evslzsmoi"
    serializer = get_meal_plan_serializer(mock_device)
    assert isinstance(serializer, Base64Encoder)


def test_get_meal_data(
    mock_device: CustomerDevice,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get_meal_data decodes meal plan correctly."""
    mock_device.product_id = "wfkzyy0evslzsmoi"
    # Set up device with encoded meal plan
    mock_device.status["meal_plan"] = "fwkAAQF/CR4BAX8MAAEBfw8AAgF/FQACAQ=="
    mock_device.function["meal_plan"] = True  # Mock function presence

    serializer = get_meal_plan_serializer(mock_device)
    assert serializer is not None

    result = serializer.get_meal_data(mock_device)
    assert result == snapshot


def test_get_meal_plan_update_commands(
    mock_device: CustomerDevice,
) -> None:
    """Test get_meal_plan_update_commands encodes data correctly."""
    mock_device.product_id = "wfkzyy0evslzsmoi"
    mock_device.function["meal_plan"] = True  # Mock function presence

    serializer = get_meal_plan_serializer(mock_device)
    assert serializer is not None

    commands = serializer.get_meal_plan_update_commands(
        mock_device, decoded_meal_plan()
    )
    assert commands == [
        {"code": "meal_plan", "value": "fwkAAQF/CR4BAX8MAAEBfw8AAgF/FQACAQ=="}
    ]


def test_get_meal_data_invalid_data(
    mock_device: CustomerDevice,
) -> None:
    """Test get_meal_data with invalid data."""
    mock_device.product_id = "wfkzyy0evslzsmoi"
    # No meal_plan in status
    mock_device.status.pop("meal_plan", None)
    mock_device.function["meal_plan"] = True

    serializer = get_meal_plan_serializer(mock_device)
    assert serializer is not None

    with pytest.raises(ValueError, match="Invalid Base64 meal plan data"):
        serializer.get_meal_data(mock_device)

    # Invalid meal_plan value
    mock_device.status["meal_plan"] = "unknown"

    with pytest.raises(ValueError, match="Invalid Base64 meal plan data"):
        serializer.get_meal_data(mock_device)


def test_get_meal_plan_update_commands_no_function(
    mock_device: CustomerDevice,
) -> None:
    """Test get_meal_plan_update_commands when meal_plan function not supported."""
    mock_device.product_id = "wfkzyy0evslzsmoi"
    # Remove meal_plan from function
    mock_device.function.pop("meal_plan", None)

    serializer = get_meal_plan_serializer(mock_device)
    assert serializer is not None

    with pytest.raises(
        ValueError,
        match="Feeder with ID device_id does not support meal plan functionality",
    ):
        serializer.get_meal_plan_update_commands(
            mock_device, decoded_meal_plan()
        )
