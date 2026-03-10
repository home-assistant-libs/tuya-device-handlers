"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.light import (
    BrightnessWrapper,
    ColorDataWrapper,
    ColorTempWrapper,
)

from . import inject_dpcode

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


def _inject_default_light(mock_device: CustomerDevice) -> None:
    inject_dpcode(
        mock_device,
        "bright_value",
        1000,
        dptype="Integer",
        values='{"min": 10, "max":1000, "scale":0, "step":1}',
    )
    inject_dpcode(
        mock_device,
        "temp_value",
        0,
        dptype="Integer",
        values='{"min": 0, "max":1000, "scale":0, "step":1}',
    )
    inject_dpcode(
        mock_device,
        "colour_data",
        '{"h": 229, "s": 1000, "v": 1000}',
        dptype="Json",
        values=(
            "{"
            '"h": {"min": 0, "max":360, "scale":0, "step":1, "unit":""},'
            '"s": {"min": 0, "max":1000, "scale":0, "step":1, "unit":""},'
            '"v": {"min": 0, "max":1000, "scale":0, "step":1, "unit":""}'
            "}"
        ),
    )


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "status_updates", "expected_device_status"),
    [
        (BrightnessWrapper, "bright_value", {"bright_value": 1000}, 255),
        (BrightnessWrapper, "bright_value", {"bright_value": 500}, 126),
        (BrightnessWrapper, "bright_value", {"bright_value": 10}, 0),
        (
            ColorDataWrapper,
            "colour_data",
            {},
            (228.6350974930362, 393.3070866141732, 1002.9330708661417),
        ),
        (ColorTempWrapper, "temp_value", {"temp_value": 0}, 2000),
        (ColorTempWrapper, "temp_value", {"temp_value": 500}, 3059),
        (ColorTempWrapper, "temp_value", {"temp_value": 1000}, 6500),
    ],
)
def test_read_device_status(
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any]],
    dpcode: str,
    status_updates: dict[str, Any],
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    _inject_default_light(mock_device)
    mock_device.status.update(status_updates)
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
    ("wrapper_type", "dpcode", "action", "expected"),
    [
        (
            BrightnessWrapper,
            "bright_value",
            255,
            [{"code": "bright_value", "value": 1000}],
        ),
        (
            BrightnessWrapper,
            "bright_value",
            126,
            [{"code": "bright_value", "value": 499}],
        ),
        (
            BrightnessWrapper,
            "bright_value",
            0,
            [{"code": "bright_value", "value": 10}],
        ),
        (
            ColorDataWrapper,
            "colour_data",
            (228.6350974930362, 393.3070866141732, 1002.9330708661417),
            [
                {
                    "code": "colour_data",
                    "value": '{"h": 229, "s": 1000, "v": 1000}',
                }
            ],
        ),
        (
            ColorTempWrapper,
            "temp_value",
            2000,
            [{"code": "temp_value", "value": 0}],
        ),
        (
            ColorTempWrapper,
            "temp_value",
            3059,
            [{"code": "temp_value", "value": 500}],
        ),
        (
            ColorTempWrapper,
            "temp_value",
            6500,
            [{"code": "temp_value", "value": 1000}],
        ),
    ],
)
def test_light_action_command(
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any]],
    dpcode: str,
    action: str,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    _inject_default_light(mock_device)
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.get_update_commands(mock_device, action) == expected
