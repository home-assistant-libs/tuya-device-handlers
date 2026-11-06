"""Test device-level quirk initialisation for the apnfmkj7hm0e3hfo heater."""

import json

from tests import create_device
from tuya_device_handlers.definition.climate import (
    get_default_definition as get_climate_definition,
)
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_panel_heater_expands_mode_range(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test apnfmkj7hm0e3hfo expands the mode enum range."""
    device = create_device("qn_apnfmkj7hm0e3hfo.json")

    assert json.loads(device.status_range["mode"].values) == {"range": ["eco"]}
    assert json.loads(device.function["mode"].values) == {"range": ["eco"]}

    filled_quirks_registry.initialise_device_quirk(device)

    expected = {"range": ["comfor", "eco"]}
    assert json.loads(device.status_range["mode"].values) == expected
    assert json.loads(device.function["mode"].values) == expected
    assert (
        json.loads(device.local_strategy[4]["config_item"]["valueDesc"])
        == expected
    )


def test_panel_heater_exposes_comfort_preset(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test the comfort preset is exposed."""
    device = create_device("qn_apnfmkj7hm0e3hfo.json")

    definition = get_climate_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == ["eco"]
    assert definition.preset_wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_climate_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition.switch_wrapper is not None
    assert definition.switch_wrapper.read_device_status(device) is True
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == ["comfor", "eco"]
    assert definition.preset_wrapper.read_device_status(device) == "comfor"
