"""Test device-level quirk initialisation for DJ lights."""

from tuya_sharing import CustomerDevice

from tests import create_device
from tuya_device_handlers.definition.light import (
    FallbackColorDataMode,
    LightDefinition,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.light import ColorTempWrapper
from tuya_device_handlers.registry import QuirksRegistry


def _light_definition(device: CustomerDevice) -> LightDefinition | None:
    return get_default_definition(
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


def test_quirk_overrides_color_temp_kelvin_range(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Smart bulb CCT is 1600-4000 K, not the Tuya default 2000-6500 K."""
    device = create_device("dj_ewxuxtzrwf4zxyqj.json")

    filled_quirks_registry.initialise_device_quirk(device)
    definition = _light_definition(device)
    assert definition is not None
    wrapper = definition.color_temp_wrapper
    assert isinstance(wrapper, ColorTempWrapper)
    assert wrapper.min_kelvin == 1600
    assert wrapper.max_kelvin == 4000
    assert wrapper.read_device_status(device) == 3059
    assert wrapper.get_update_commands(device, 1600) == [
        {"code": "temp_value_v2", "value": 0}
    ]
    assert wrapper.get_update_commands(device, 4000) == [
        {"code": "temp_value_v2", "value": 1000}
    ]
