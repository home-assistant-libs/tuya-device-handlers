"""Test device-level quirk initialisation."""

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk registers the temperature, humidity, unit and battery DPs."""
    device = create_device("tdq_xeagimantb7d7apb.json")

    assert "temp_unit_convert" not in device.status_range
    assert "temp_current" not in device.status_range
    assert "humidity_value" not in device.status_range
    assert "battery_state" not in device.status_range
    assert "temp_unit_convert" not in device.function

    filled_quirks_registry.initialise_device_quirk(device)

    assert "temp_unit_convert" in device.status_range
    assert "temp_current" in device.status_range
    assert "humidity_value" in device.status_range
    assert "battery_state" in device.status_range
    assert "temp_unit_convert" in device.function


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """TDQ quirk registers explicit sensor device classes."""
    device = create_device("tdq_xeagimantb7d7apb.json")

    definitions = get_sensor_default_definitions(device)
    assert "temp_current" not in definitions
    assert "humidity_value" not in definitions
    assert "battery_state" not in definitions

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert "temp_current" in definitions
    assert "humidity_value" in definitions
    assert "battery_state" in definitions
