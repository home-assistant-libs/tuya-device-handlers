"""Test DeviceWrapper classes."""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.common import (
    DPCodeIntegerWrapper,
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.light import (
    BrightnessWrapper,
    ColorDataWrapper,
    ColorTempWrapper,
)
from tuya_device_handlers.utils import RemapHelper

from . import inject_dpcode


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
    (
        "sample",
        "wrapper_type",
        "dpcode",
        "status_updates",
        "expected_device_status",
    ),
    [
        (
            "default",
            BrightnessWrapper,
            "bright_value",
            {"bright_value": 1000},
            255,
        ),
        (
            "default",
            BrightnessWrapper,
            "bright_value",
            {"bright_value": 500},
            126,
        ),
        (
            "default",
            BrightnessWrapper,
            "bright_value",
            {"bright_value": 10},
            0,
        ),
        (
            "default",
            ColorDataWrapper,
            "colour_data",
            {},
            (228.6350974930362, 393.3070866141732, 1002.9330708661417),
        ),
        ("default", ColorTempWrapper, "temp_value", {"temp_value": 0}, 2000),
        ("default", ColorTempWrapper, "temp_value", {"temp_value": 500}, 3059),
        ("default", ColorTempWrapper, "temp_value", {"temp_value": 1000}, 6500),
        # Note: extended_brightness is here for coverage, but we never got
        # diagnostic data to validate
        (
            "extended_brightness",
            BrightnessWrapper,
            "bright_value_1",
            {"bright_value_1": 1000},
            255,
        ),
        (
            "extended_brightness",
            BrightnessWrapper,
            "bright_value_1",
            {"bright_value_1": 500},
            126,
        ),
        (
            "extended_brightness",
            BrightnessWrapper,
            "bright_value_1",
            {"bright_value_1": 10},
            0,
        ),
    ],
)
def test_read_device_status(
    sample: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    dpcode: str,
    status_updates: dict[str, Any],
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    if sample == "default":
        _inject_default_light(mock_device)
    elif sample == "extended_brightness":
        inject_dpcode(
            mock_device,
            "bright_value_1",
            1000,
            dptype="Integer",
            values='{"min": 10, "max":1000, "scale":0, "step":1}',
        )
        inject_dpcode(
            mock_device,
            "brightness_max_1",
            1000,
            dptype="Integer",
            values='{"min": 10, "max":1000, "scale":0, "step":1}',
        )
        inject_dpcode(
            mock_device,
            "brightness_min_1",
            10,
            dptype="Integer",
            values='{"min": 10, "max":1000, "scale":0, "step":1}',
        )
    mock_device.status.update(status_updates)
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    if sample == "extended_brightness":
        brightness_wrapper = wrapper
        assert isinstance(brightness_wrapper, BrightnessWrapper)
        brightness_wrapper.brightness_max = DPCodeIntegerWrapper.find_dpcode(
            mock_device, "brightness_max_1"
        )
        assert isinstance(
            brightness_wrapper.brightness_max, DPCodeIntegerWrapper
        )
        brightness_wrapper.brightness_max_remap = (
            RemapHelper.from_type_information(
                brightness_wrapper.brightness_max.type_information, 0, 255
            )
        )
        brightness_wrapper.brightness_min = DPCodeIntegerWrapper.find_dpcode(
            mock_device, "brightness_min_1"
        )
        assert isinstance(
            brightness_wrapper.brightness_min, DPCodeIntegerWrapper
        )
        brightness_wrapper.brightness_min_remap = (
            RemapHelper.from_type_information(
                brightness_wrapper.brightness_min.type_information, 0, 255
            )
        )

    assert wrapper.read_device_status(mock_device) == expected_device_status

    # All wrappers return None if status is None
    mock_device.status[dpcode] = None
    assert wrapper.read_device_status(mock_device) is None

    # All wrappers return None if status is missing
    mock_device.status.pop(dpcode)
    assert wrapper.read_device_status(mock_device) is None


@pytest.mark.parametrize(
    ("sample", "wrapper_type", "dpcode", "action", "expected"),
    [
        (
            "default",
            BrightnessWrapper,
            "bright_value",
            255,
            [{"code": "bright_value", "value": 1000}],
        ),
        (
            "default",
            BrightnessWrapper,
            "bright_value",
            126,
            [{"code": "bright_value", "value": 499}],
        ),
        (
            "default",
            BrightnessWrapper,
            "bright_value",
            0,
            [{"code": "bright_value", "value": 10}],
        ),
        (
            "default",
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
            "default",
            ColorTempWrapper,
            "temp_value",
            2000,
            [{"code": "temp_value", "value": 0}],
        ),
        (
            "default",
            ColorTempWrapper,
            "temp_value",
            3059,
            [{"code": "temp_value", "value": 500}],
        ),
        (
            "default",
            ColorTempWrapper,
            "temp_value",
            6500,
            [{"code": "temp_value", "value": 1000}],
        ),
        # Note: extended_brightness is here for coverage, but we never got
        # diagnostic data to validate
        (
            "extended_brightness",
            BrightnessWrapper,
            "bright_value_1",
            255,
            [{"code": "bright_value_1", "value": 1000}],
        ),
        (
            "extended_brightness",
            BrightnessWrapper,
            "bright_value_1",
            126,
            [{"code": "bright_value_1", "value": 499}],
        ),
        (
            "extended_brightness",
            BrightnessWrapper,
            "bright_value_1",
            0,
            [{"code": "bright_value_1", "value": 10}],
        ),
    ],
)
def test_light_action_command(
    sample: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    dpcode: str,
    action: str,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    if sample == "default":
        _inject_default_light(mock_device)
    elif sample == "extended_brightness":
        inject_dpcode(
            mock_device,
            "bright_value_1",
            1000,
            dptype="Integer",
            values='{"min": 10, "max":1000, "scale":0, "step":1}',
        )
        inject_dpcode(
            mock_device,
            "brightness_max_1",
            1000,
            dptype="Integer",
            values='{"min": 10, "max":1000, "scale":0, "step":1}',
        )
        inject_dpcode(
            mock_device,
            "brightness_min_1",
            10,
            dptype="Integer",
            values='{"min": 10, "max":1000, "scale":0, "step":1}',
        )
    _inject_default_light(mock_device)
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    if sample == "extended_brightness":
        brightness_wrapper = wrapper
        assert isinstance(brightness_wrapper, BrightnessWrapper)
        brightness_wrapper.brightness_max = DPCodeIntegerWrapper.find_dpcode(
            mock_device, "brightness_max_1"
        )
        assert isinstance(
            brightness_wrapper.brightness_max, DPCodeIntegerWrapper
        )
        brightness_wrapper.brightness_max_remap = (
            RemapHelper.from_type_information(
                brightness_wrapper.brightness_max.type_information, 0, 255
            )
        )
        brightness_wrapper.brightness_min = DPCodeIntegerWrapper.find_dpcode(
            mock_device, "brightness_min_1"
        )
        assert isinstance(
            brightness_wrapper.brightness_min, DPCodeIntegerWrapper
        )
        brightness_wrapper.brightness_min_remap = (
            RemapHelper.from_type_information(
                brightness_wrapper.brightness_min.type_information, 0, 255
            )
        )
    assert wrapper.get_update_commands(mock_device, action) == expected
