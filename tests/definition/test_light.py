"""Tests for light definition."""

from tests import create_device
from tuya_device_handlers.definition.light import (
    FallbackColorDataMode,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.common import (
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
)
from tuya_device_handlers.device_wrapper.light import (
    BrightnessWrapper,
    ColorDataWrapper,
)


def test_get_default_definition() -> None:
    """Test get_default_definition."""
    device = create_device("dj_mki13ie507rlry4r.json")
    assert (
        definition := get_default_definition(
            device,
            switch_dpcode="switch_led",
            brightness_dpcode=("bright_value_v2", "bright_value"),
            brightness_max_dpcode=None,
            brightness_min_dpcode=None,
            color_data_dpcode=("colour_data_v2", "colour_data"),
            color_mode_dpcode="work_mode",
            color_temp_dpcode=("temp_value_v2", "temp_value"),
            fallback_color_data_mode=FallbackColorDataMode.V1,
        )
    )
    assert isinstance(definition.brightness_wrapper, BrightnessWrapper)
    assert isinstance(definition.color_data_wrapper, ColorDataWrapper)
    assert isinstance(definition.color_mode_wrapper, DPCodeEnumWrapper)
    assert not definition.color_temp_wrapper
    assert isinstance(definition.switch_wrapper, DPCodeBooleanWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition."""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert not get_default_definition(
        device,
        switch_dpcode="bad",
        brightness_dpcode=None,
        brightness_max_dpcode=None,
        brightness_min_dpcode=None,
        color_data_dpcode=None,
        color_mode_dpcode=None,
        color_temp_dpcode=None,
        fallback_color_data_mode=FallbackColorDataMode.V1,
    )


def test_missing_colour_data_hsv() -> None:
    """Test missing_colour_data_hsv."""
    device = create_device("jsq_op2lzjcj7fdfhid8.json")
    assert (
        definition := get_default_definition(
            device,
            switch_dpcode="switch_led",
            brightness_dpcode="bright_value",
            brightness_max_dpcode=None,
            brightness_min_dpcode=None,
            color_data_dpcode="colour_data_hsv",
            color_mode_dpcode=None,
            color_temp_dpcode=None,
            fallback_color_data_mode=FallbackColorDataMode.V1,
        )
    )
    assert definition.brightness_wrapper is None
    assert isinstance(definition.color_data_wrapper, ColorDataWrapper)
    assert definition.color_mode_wrapper is None
    assert definition.color_temp_wrapper is None
    assert isinstance(definition.switch_wrapper, DPCodeBooleanWrapper)
