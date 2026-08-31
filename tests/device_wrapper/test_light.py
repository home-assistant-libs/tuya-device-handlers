"""Test DeviceWrapper classes."""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.const import ColorTempScale
from tuya_device_handlers.device_wrapper.common import (
    DPCodeIntegerWrapper,
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.light import (
    BrightnessWrapper,
    ColorDataJsonWrapper,
    ColorDataStringWrapper,
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
            ColorDataJsonWrapper,
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
            ColorDataJsonWrapper,
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


def _inject_hex_string_light(mock_device: CustomerDevice) -> None:
    """Inject a light whose colour_data is a hex-encoded String DP."""
    inject_dpcode(
        mock_device,
        "colour_data",
        "007803e803e8",
        dptype="String",
        values='{"maxlen": 255}',
    )


@pytest.mark.parametrize(
    ("status", "expected_device_status"),
    [
        (
            "007800800040",
            (119.33147632311977, 50.0, 63.24803149606299),
        ),
        ("00b400ff0080", (179.49860724233983, 100.0, 127.5)),
    ],
)
def test_color_data_string_read_device_status(
    status: str,
    expected_device_status: tuple[float, float, float],
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status for hex-encoded String colour_data."""
    _inject_hex_string_light(mock_device)
    mock_device.status["colour_data"] = status
    wrapper = ColorDataStringWrapper.find_dpcode(mock_device, "colour_data")

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status


@pytest.mark.parametrize(
    "status",
    [
        # Non-hexadecimal, but correctly sized
        "zzzzzzzzzzzz",
        # Wrongly sized
        "0078",
        "",
        # Not a string at all
        None,
        123456,
    ],
)
def test_color_data_string_invalid_status(
    status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test unusable hex-encoded String colour_data values return None."""
    _inject_hex_string_light(mock_device)
    wrapper = ColorDataStringWrapper.find_dpcode(mock_device, "colour_data")

    assert wrapper
    mock_device.status["colour_data"] = status
    assert wrapper.read_device_status(mock_device) is None


def test_color_data_string_missing_status(mock_device: CustomerDevice) -> None:
    """Test a missing hex-encoded String colour_data returns None."""
    _inject_hex_string_light(mock_device)
    wrapper = ColorDataStringWrapper.find_dpcode(mock_device, "colour_data")

    assert wrapper
    mock_device.status.pop("colour_data")
    assert wrapper.read_device_status(mock_device) is None


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        (
            (119.33147632311977, 50.0, 63.24803149606299),
            [{"code": "colour_data", "value": "007800800040"}],
        ),
        (
            (179.49860724233983, 100.0, 127.5),
            [{"code": "colour_data", "value": "00b400ff0080"}],
        ),
    ],
)
def test_color_data_string_action_command(
    action: tuple[float, float, float],
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands for hex-encoded String colour_data."""
    _inject_hex_string_light(mock_device)
    wrapper = ColorDataStringWrapper.find_dpcode(mock_device, "colour_data")

    assert wrapper
    assert wrapper.get_update_commands(mock_device, action) == expected


def test_color_temp_wrapper_default_kelvin_range(
    mock_device: CustomerDevice,
) -> None:
    """Test the default color temperature range of a light."""
    _inject_default_light(mock_device)
    wrapper = ColorTempWrapper.find_dpcode(mock_device, "temp_value")

    assert wrapper
    assert wrapper.min_kelvin == 2000
    assert wrapper.max_kelvin == 6500


def test_color_temp_wrapper_custom_kelvin_range(
    mock_device: CustomerDevice,
) -> None:
    """Test a subclass overriding the color temperature range."""

    class CustomColorTempWrapper(ColorTempWrapper):
        """Wrapper for a 1600-4000 K lamp."""

        min_kelvin = 1600
        max_kelvin = 4000

    _inject_default_light(mock_device)
    mock_device.status["temp_value"] = 795
    wrapper = CustomColorTempWrapper.find_dpcode(mock_device, "temp_value")

    assert wrapper
    assert wrapper.min_kelvin == 1600
    assert wrapper.max_kelvin == 4000
    assert wrapper.read_device_status(mock_device) == 3059
    assert wrapper.get_update_commands(mock_device, 4000) == [
        {"code": "temp_value", "value": 1000}
    ]


@pytest.mark.parametrize(
    ("raw_value", "expected_kelvin"),
    [
        (0, 1600),
        (795, 3508),
        (1000, 4000),
    ],
)
def test_color_temp_wrapper_kelvin_scale_read(
    mock_device: CustomerDevice,
    raw_value: int,
    expected_kelvin: int,
) -> None:
    """Test reading a device whose raw range is linear in Kelvin."""

    class KelvinScaleWrapper(ColorTempWrapper):
        """Wrapper for a 1600-4000 K lamp, linear in Kelvin."""

        min_kelvin = 1600
        max_kelvin = 4000
        color_temp_scale = ColorTempScale.KELVIN

    _inject_default_light(mock_device)
    mock_device.status["temp_value"] = raw_value
    wrapper = KelvinScaleWrapper.find_dpcode(mock_device, "temp_value")

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_kelvin


@pytest.mark.parametrize(
    ("kelvin", "expected_raw"),
    [
        (1600, 0),
        (3508, 795),
        (4000, 1000),
    ],
)
def test_color_temp_wrapper_kelvin_scale_write(
    mock_device: CustomerDevice,
    kelvin: int,
    expected_raw: int,
) -> None:
    """Test writing to a device whose raw range is linear in Kelvin."""

    class KelvinScaleWrapper(ColorTempWrapper):
        """Wrapper for a 1600-4000 K lamp, linear in Kelvin."""

        min_kelvin = 1600
        max_kelvin = 4000
        color_temp_scale = ColorTempScale.KELVIN

    _inject_default_light(mock_device)
    wrapper = KelvinScaleWrapper.find_dpcode(mock_device, "temp_value")

    assert wrapper
    assert wrapper.get_update_commands(mock_device, kelvin) == [
        {"code": "temp_value", "value": expected_raw}
    ]


def test_color_temp_wrapper_default_scale(mock_device: CustomerDevice) -> None:
    """Test the default color temperature scale of a light."""
    _inject_default_light(mock_device)
    wrapper = ColorTempWrapper.find_dpcode(mock_device, "temp_value")

    assert wrapper
    assert wrapper.color_temp_scale is ColorTempScale.MIRED
