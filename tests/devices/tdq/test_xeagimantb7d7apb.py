"""Test device-level quirk initialisation."""

from tests import create_device
from tests.integration_helpers.sensor import (
    get_sensor_default_definitions,
    get_sensor_wrapper,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_sensor_device_class_override_tdq(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """TDQ quirk registers explicit sensor device classes."""
    device = create_device("tdq_xeagimantb7d7apb.json")

    definitions = get_sensor_default_definitions(device)
    assert get_sensor_wrapper(definitions, "temp_current") is None
    assert get_sensor_wrapper(definitions, "humidity_value") is None
    assert get_sensor_wrapper(definitions, "battery_state") is None

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert get_sensor_wrapper(definitions, "temp_current") is not None
    assert get_sensor_wrapper(definitions, "humidity_value") is not None
    assert get_sensor_wrapper(definitions, "battery_state") is not None
