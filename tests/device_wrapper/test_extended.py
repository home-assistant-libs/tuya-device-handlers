"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedBooleanWrapper,
    DPCodeInvertedPercentageWrapper,
    DPCodePercentageWrapper,
    DPCodeRoundedIntegerWrapper,
)

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "status", "expected_device_status"),
    [
        (DPCodeRoundedIntegerWrapper, "demo_integer", 0, 0),
        (DPCodeRoundedIntegerWrapper, "demo_integer", 123, 12),
        (DPCodePercentageWrapper, "demo_integer", 0, 0),
        (DPCodePercentageWrapper, "demo_integer", 123, 12),
        (DPCodeInvertedPercentageWrapper, "demo_integer", 0, 100),
        (DPCodeInvertedPercentageWrapper, "demo_integer", 123, 88),
        (DPCodeInvertedBooleanWrapper, "demo_boolean", True, False),
        (DPCodeInvertedBooleanWrapper, "demo_boolean", False, True),
    ],
)
def test_read_device_status(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    status: Any,
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    mock_device.status[dpcode] = status
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status

    # All wrappers return None if status is None
    mock_device.status[dpcode] = None
    assert wrapper.read_device_status(mock_device) is None

    # All wrappers return None if status is missing
    mock_device.status.pop(dpcode)
    assert wrapper.read_device_status(mock_device) is None


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "value", "expected"),
    [
        (
            DPCodePercentageWrapper,
            "demo_integer",
            11.3,
            [{"code": "demo_integer", "value": 113}],
        ),
        (
            DPCodeInvertedPercentageWrapper,
            "demo_integer",
            11.3,
            [{"code": "demo_integer", "value": 887}],
        ),
        (
            DPCodeInvertedBooleanWrapper,
            "demo_boolean",
            False,
            [{"code": "demo_boolean", "value": True}],
        ),
    ],
)
def test_get_update_commands(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    value: Any,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.get_update_commands(mock_device, value) == expected
