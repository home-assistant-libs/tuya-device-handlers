"""Test device-level quirk initialisation for QN devices."""

import json

from tests import create_device
from tuya_device_handlers.definition.climate import (
    get_default_definition as get_climate_definition,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaClimateHVACMode,
    TuyaUnitOfTemperature,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_heater_expands_mode_range(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test tjvnxyobs3upidjo expands the mode enum range."""
    device = create_device("qn_tjvnxyobs3upidjo.json")

    assert json.loads(device.status_range["mode"].values) == {"range": ["eco"]}
    assert json.loads(device.function["mode"].values) == {"range": ["eco"]}

    filled_quirks_registry.initialise_device_quirk(device)

    expected = {"range": ["eco", "off"]}
    assert json.loads(device.status_range["mode"].values) == expected
    assert json.loads(device.function["mode"].values) == expected
    assert (
        json.loads(device.local_strategy[4]["config_item"]["valueDesc"])
        == expected
    )


def test_heater_exposes_off_hvac_mode(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test the expanded mode range exposes an off HVAC mode."""
    device = create_device("qn_tjvnxyobs3upidjo.json")

    definition = get_climate_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == []
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == ["eco"]

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_climate_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == [TuyaClimateHVACMode.OFF]
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == ["eco"]
