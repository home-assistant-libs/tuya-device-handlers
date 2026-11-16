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
    device = create_device("kt_uzysooabradqagui.json")

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.FAHRENHEIT
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 68
    assert set_temperature_wrapper.native_unit == "℃"

    filled_quirks_registry.initialise_device_quirk(device)

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.FAHRENHEIT
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 68
    assert set_temperature_wrapper.native_unit == "℉"
    assert set_temperature_wrapper.min_value == 61
    assert set_temperature_wrapper.max_value == 88
    assert "temp_set_f" not in device.status_range
    assert "temp_set_f" not in device.function


def test_celsius_variant_is_left_untouched(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test the quirk leaves a Celsius variant of the same product_id alone.

    No Celsius capture is available for this product_id, so the Fahrenheit
    fixture is reused with a Celsius setpoint (22.0 ℃).
    """
    device = create_device("kt_uzysooabradqagui.json")
    device.status["temp_set"] = 220

    filled_quirks_registry.initialise_device_quirk(device)

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.CELSIUS
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 22
    assert set_temperature_wrapper.native_unit == "℃"
    assert "temp_set_f" in device.status_range
    assert "temp_set_f" in device.function
