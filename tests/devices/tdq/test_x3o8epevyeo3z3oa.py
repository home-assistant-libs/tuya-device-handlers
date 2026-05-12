"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.sensor import get_default_definition
from tuya_device_handlers.registry import QuirksRegistry


def test_sensor_device_class_override_tdq(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """TDQ quirk registers explicit sensor device classes."""
    device = create_device("tdq_x3o8epevyeo3z3oa.json")
    assert get_default_definition(device, "temp_current") is None
    assert get_default_definition(device, "humidity_value") is None
    assert get_default_definition(device, "battery_state") is None

    filled_quirks_registry.initialise_device_quirk(device)

    assert get_default_definition(device, "temp_current") is not None
    assert get_default_definition(device, "humidity_value") is not None
    assert get_default_definition(device, "battery_state") is not None
