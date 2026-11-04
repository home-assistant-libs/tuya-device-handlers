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
    """Test quirk adds the missing `heat` mode value."""
    device = create_device("wk_qn4upx5kzja3rg1l.json")
    assert device.status["mode"] == "heat"

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == [
        TuyaClimateHVACMode.HEAT_COOL
    ]
    assert definition.hvac_mode_wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == [
        TuyaClimateHVACMode.HEAT_COOL,
        TuyaClimateHVACMode.HEAT,
    ]
    assert (
        definition.hvac_mode_wrapper.read_device_status(device)
        == TuyaClimateHVACMode.HEAT
    )
