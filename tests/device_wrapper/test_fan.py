"""Test DeviceWrapper classes."""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.fan import (
    FanDirectionEnumWrapper,
    FanSpeedEnumWrapper,
    FanSpeedIntegerWrapper,
)
from tuya_device_handlers.helpers.homeassistant import TuyaFanDirection

from . import inject_dpcode


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "status", "expected_device_status"),
    [
        (FanDirectionEnumWrapper, "direction", "scene", None),
        (
            FanDirectionEnumWrapper,
            "direction",
            "forward",
            TuyaFanDirection.FORWARD,
        ),
        (
            FanDirectionEnumWrapper,
            "direction",
            "reverse",
            TuyaFanDirection.REVERSE,
        ),
        (FanSpeedEnumWrapper, "demo_enum", "scene", 33),
        (FanSpeedEnumWrapper, "demo_enum", "customize_scene", 66),
        (FanSpeedEnumWrapper, "demo_enum", "other", None),
        (FanSpeedIntegerWrapper, "demo_integer", 0, 1),
        (FanSpeedIntegerWrapper, "demo_integer", 123, 13),
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
    inject_dpcode(
        mock_device,
        "direction",
        "chargego",
        dptype="Enum",
        values='{"range": ["forward","reverse"]}',
    )
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
            FanSpeedEnumWrapper,
            "demo_enum",
            10,
            [{"code": "demo_enum", "value": "scene"}],
        ),
        (
            FanSpeedEnumWrapper,
            "demo_enum",
            90,
            [{"code": "demo_enum", "value": "colour"}],
        ),
        (
            FanSpeedEnumWrapper,
            "demo_enum",
            500,  # not a valid value - maps last value
            [{"code": "demo_enum", "value": "colour"}],
        ),
        (
            FanSpeedIntegerWrapper,
            "demo_integer",
            11.3,
            [{"code": "demo_integer", "value": 104}],
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
