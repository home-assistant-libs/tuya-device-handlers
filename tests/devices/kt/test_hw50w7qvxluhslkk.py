"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import (
    get_default_definition as get_climate_definition,
)
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_fahrenheit_variant(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test the quirk fixes the unit on a Fahrenheit variant."""
    device = create_device("kt_hw50w7qvxluhslkk.json")

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.FAHRENHEIT
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 65
    assert set_temperature_wrapper.native_unit == "℃"

    filled_quirks_registry.initialise_device_quirk(device)

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.FAHRENHEIT
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 65
    assert set_temperature_wrapper.native_unit == "℉"
    assert "temp_set_f" not in device.status_range
    assert "temp_set_f" not in device.function


def test_celsius_variant_is_left_untouched(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test the quirk leaves a Celsius variant of the same product_id alone.

    This product_id is shared with units that report temp_set in Celsius.
    The quirk should only apply to the Fahrenheit variants (see #385).
    """
    device = create_device("kt_hw50w7qvxluhslkk_celsius.json")

    filled_quirks_registry.initialise_device_quirk(device)

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.CELSIUS
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 26
    assert set_temperature_wrapper.native_unit == "℃"
    assert "temp_set_f" in device.status_range
    assert "temp_set_f" in device.function
