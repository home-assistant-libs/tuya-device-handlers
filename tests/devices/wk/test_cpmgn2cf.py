"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.sensor import get_default_definition
from tuya_device_handlers.registry import QuirksRegistry


def test_valve_sensor_wk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """WK quirk registers the valve datapoint as a sensor."""
    device = create_device("wk_cpmgn2cf.json")
    assert get_default_definition(device, "valve") is None

    filled_quirks_registry.initialise_device_quirk(device)

    assert get_default_definition(device, "valve") is not None
