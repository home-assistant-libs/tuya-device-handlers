"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import (
    get_default_definition as get_climate_definition,
)
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_default_definition(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing datapoints."""
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


def test_celsius_variant_is_forced_to_fahrenheit(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Document the current bug on a Celsius variant of the same product_id.

    This product_id is shared with units that report temp_set in Celsius.
    The quirk forces the unit to Fahrenheit for all of them, so a Celsius
    device ends up with the wrong unit (see #385).
    """
    device = create_device("kt_hw50w7qvxluhslkk_celsius.json")

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.CELSIUS
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 26
    assert set_temperature_wrapper.native_unit == "℃"

    filled_quirks_registry.initialise_device_quirk(device)

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.CELSIUS
    )
    assert climate_definition is not None
    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    # The device reports 26°C, but the quirk relabels it as Fahrenheit.
    assert set_temperature_wrapper.native_unit == "℉"
