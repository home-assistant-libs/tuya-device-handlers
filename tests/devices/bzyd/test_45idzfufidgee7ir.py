"""Tests for the Momcozy Smart White Noise Machine (bzyd) quirk.

The device reports colour_data with saturation and value on a 0-1000
scale, while its Json datapoint declares no ranges, so the default
definition falls back to a 0-255 scale. Without the quirk, every colour
preset comes out washed out and dim.

See https://github.com/home-assistant/core/issues/188634.
"""

from unittest.mock import patch

from tuya_sharing import CustomerDevice

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.definition.light import (
    FallbackColorDataMode,
    LightDefinition,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.light import ColorDataJsonWrapper
from tuya_device_handlers.registry import QuirksRegistry


def _light_definition(device: CustomerDevice) -> LightDefinition | None:
    return get_default_definition(
        device,
        switch_dpcode="switch_led",
        brightness_dpcode=None,
        brightness_max_dpcode=None,
        brightness_min_dpcode=None,
        color_data_dpcode="colour_data",
        color_mode_dpcode="work_mode",
        color_temp_dpcode=None,
        fallback_color_data_mode=FallbackColorDataMode.V1,
    )


def test_quirk_encodes_colour_data_on_1000_scale(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Without the quirk colour_data is capped at 255, with it on 0-1000."""
    device = create_device("bzyd_45idzfufidgee7ir.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definition = _light_definition(device)
    assert definition is not None
    wrapper = definition.color_data_wrapper
    assert isinstance(wrapper, ColorDataJsonWrapper)
    assert wrapper.get_update_commands(device, (120.0, 100.0, 255.0)) == [
        {"code": "colour_data", "value": '{"h": 121, "s": 255, "v": 255}'}
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    definition = _light_definition(device)
    assert definition is not None
    wrapper = definition.color_data_wrapper
    assert isinstance(wrapper, ColorDataJsonWrapper)
    assert wrapper.get_update_commands(device, (120.0, 100.0, 255.0)) == [
        {"code": "colour_data", "value": '{"h": 120, "s": 1000, "v": 1000}'}
    ]
    assert wrapper.get_update_commands(device, (360.0, 100.0, 255.0)) == [
        {"code": "colour_data", "value": '{"h": 360, "s": 1000, "v": 1000}'}
    ]


def test_quirk_reads_cloud_status(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With the quirk, the cloud's colour_data status reads on HA scales."""
    device = create_device("bzyd_45idzfufidgee7ir.json")

    filled_quirks_registry.initialise_device_quirk(device)
    definition = _light_definition(device)
    assert definition is not None
    wrapper = definition.color_data_wrapper
    assert isinstance(wrapper, ColorDataJsonWrapper)
    assert wrapper.read_device_status(device) == (240.0, 100.0, 255.0)

    device.status["colour_data"] = '{"h": 0, "s": 0, "v": 0}'
    assert wrapper.read_device_status(device) == (0.0, 0.0, 0.0)

    device.status["colour_data"] = '{"h": 360, "s": 1000, "v": 1000}'
    assert wrapper.read_device_status(device) == (360.0, 100.0, 255.0)
