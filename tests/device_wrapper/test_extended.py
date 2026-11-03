"""Test DeviceWrapper classes."""

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
from tuya_device_handlers.device_wrapper.sensor import (
    ElectricityCurrentRawWrapper,
)

from . import inject_dpcode, inject_dpcode_function, inject_dpcode_status_range


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


@pytest.mark.parametrize(
    ("prefer_function", "expected"),
    [(False, '{"source":"status_range"}'), (True, '{"source":"function"}')],
)
def test_parsed_attribute_default_lookup(
    mock_device: CustomerDevice, prefer_function: bool, expected: str
) -> None:
    """Default candidate lookup preserves class and preferred schema."""
    inject_dpcode(
        mock_device, "phase_1", "Ag8I/QAETAAA0gAAMgAA3F8A", dptype="Raw"
    )
    inject_dpcode_status_range(
        mock_device, "phase_1", "Raw", '{"source":"status_range"}'
    )
    inject_dpcode_function(
        mock_device, "phase_1", "Raw", '{"source":"function"}'
    )
    wrapper = ElectricityCurrentRawWrapper.find_dpcode(
        mock_device, "phase_1", prefer_function=prefer_function
    )
    assert type(wrapper) is ElectricityCurrentRawWrapper
    assert wrapper.type_information.type_data == expected
    assert wrapper.read_device_status(mock_device) == 1100
