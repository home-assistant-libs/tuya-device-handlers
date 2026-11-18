"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import (
    get_default_definition as get_climate_definition,
)
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides_category(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk overrides the category and leaves the datapoints untouched."""
    device = create_device("jg_z3srxdwcicg3bla4.json")
    assert device.category == "jg"
    function = dict(device.function)
    status_range = dict(device.status_range)

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "kt"
    assert device.function == function
    assert device.status_range == status_range


def test_climate_definition(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The cooler datapoints fit the default climate definition."""
    device = create_device("jg_z3srxdwcicg3bla4.json")
    filled_quirks_registry.initialise_device_quirk(device)

    climate_definition = get_climate_definition(
        device, TuyaUnitOfTemperature.CELSIUS
    )
    assert climate_definition is not None
    assert climate_definition.temperature_unit == TuyaUnitOfTemperature.CELSIUS

    switch_wrapper = climate_definition.switch_wrapper
    assert switch_wrapper is not None
    assert switch_wrapper.read_device_status(device) is True

    current_temperature_wrapper = climate_definition.current_temperature_wrapper
    assert current_temperature_wrapper is not None
    assert current_temperature_wrapper.read_device_status(device) == 11

    set_temperature_wrapper = climate_definition.set_temperature_wrapper
    assert set_temperature_wrapper is not None
    assert set_temperature_wrapper.read_device_status(device) == 11
    assert set_temperature_wrapper.native_unit == "℃"
    assert set_temperature_wrapper.min_value == 5
    assert set_temperature_wrapper.max_value == 20

    # The cooler has no mode datapoint: it is either off or cooling.
    assert climate_definition.hvac_mode_wrapper is None
    assert climate_definition.preset_wrapper is None
