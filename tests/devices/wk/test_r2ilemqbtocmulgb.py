"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk rescales temp_current (reported in tenths of a degree)."""
    device = create_device("wk_r2ilemqbtocmulgb.json")
    assert device.status["temp_current"] == 125

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.current_temperature_wrapper is not None
    # Advertised as scale 0 / max 50, so 125 is rejected as out of range
    assert (
        definition.current_temperature_wrapper.read_device_status(device)
        is None
    )

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.current_temperature_wrapper is not None
    assert (
        definition.current_temperature_wrapper.read_device_status(device)
        == 12.5
    )
