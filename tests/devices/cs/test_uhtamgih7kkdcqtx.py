"""Test device-level quirk initialisation for CS devices."""

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """DH-24 Nexi ION UV Wifi registers the indoor temperature/humidity DPs."""
    device = create_device("cs_uhtamgih7kkdcqtx.json")

    assert "humidity_indoor" not in device.status_range
    assert "temp_indoor" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert "humidity_indoor" in device.status_range
    assert "temp_indoor" in device.status_range


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """DH-24 Nexi ION UV Wifi exposes indoor temperature/humidity sensors."""
    device = create_device("cs_uhtamgih7kkdcqtx.json")

    definitions = get_sensor_default_definitions(device)
    assert "humidity_indoor" not in definitions
    assert "temp_indoor" not in definitions

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert "humidity_indoor" in definitions
    assert "temp_indoor" in definitions
