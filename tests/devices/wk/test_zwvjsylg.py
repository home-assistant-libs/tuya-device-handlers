"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.helpers.homeassistant import (
    TuyaClimateHVACMode,
    TuyaUnitOfTemperature,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing `comfort` and `off` mode values."""
    device = create_device("wk_zwvjsylg.json")

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == []
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == ["eco"]

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == [TuyaClimateHVACMode.OFF]
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == ["eco", "comfort"]
