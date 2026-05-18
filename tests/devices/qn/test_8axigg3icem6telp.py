"""Tests for Convector Heater quirk."""

from tests import create_device
from tuya_device_handlers.definition.climate import (
    get_default_definition as get_default_climate_definition,
)
from tuya_device_handlers.definition.switch import (
    get_default_definition as get_default_switch_definition,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaClimateHVACMode,
    TuyaUnitOfTemperature,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_qn_8axigg3icem6telp_quirk_registration(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test that the quirk is properly registered."""
    device = create_device("qn_8axigg3icem6telp.json")

    assert get_default_switch_definition(device, "anion") is not None
    climate_definition = get_default_climate_definition(
        device, TuyaUnitOfTemperature.FAHRENHEIT
    )
    assert climate_definition is not None
    assert climate_definition.hvac_mode_wrapper is not None
    assert climate_definition.hvac_mode_wrapper.options == [
        TuyaClimateHVACMode.HEAT_COOL
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    # After initialisation, the "anion" switch should be removed
    # (renamed to "turbo")
    assert get_default_switch_definition(device, "anion") is None

    # The climate definition should now have the correct HVAC modes
    climate_definition = get_default_climate_definition(
        device, TuyaUnitOfTemperature.FAHRENHEIT
    )
    assert climate_definition is not None
    assert climate_definition.hvac_mode_wrapper is not None
    assert climate_definition.hvac_mode_wrapper.options == [
        TuyaClimateHVACMode.HEAT_COOL,
        TuyaClimateHVACMode.OFF,
    ]
