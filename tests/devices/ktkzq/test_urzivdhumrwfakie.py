"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk."""
    device = create_device("ktkzq_urzivdhumrwfakie.json")

    # Before quirk: category is ktkzq, no climate definition
    assert device.category == "ktkzq"
    assert "temp_set" in device.function
    assert "temp_current" in device.status_range
    assert "child_lock" in device.function

    filled_quirks_registry.initialise_device_quirk(device)

    # After quirk: category should be overridden to wk
    assert device.category == "wk"

    # Check climate definition
    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.current_temperature_wrapper is not None
    assert definition.set_temperature_wrapper is not None
    assert definition.switch_wrapper is not None
    assert definition.hvac_mode_wrapper is None  # No mode dpcode

    # Check that temp_set is writable
    assert "temp_set" in device.function
    assert "temp_set" in device.status_range

    # Check that child_lock is present
    assert "child_lock" in device.function
    assert "child_lock" in device.status_range

    # Check that switch (power_switch) is present
    assert "switch" in device.function
    assert "switch" in device.status_range
