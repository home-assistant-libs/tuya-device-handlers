"""Test device-level quirk initialisation for CS devices."""

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_dehumidifier_remaps_humidity_and_temperature(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test DH-24 Nexi ION UV Wifi remaps custom DP codes."""
    device = create_device("cs_uhtamgih7kkdcqtx.json")

    assert "humidity_indoor" not in device.status_range
    assert "temp_indoor" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert "humidity_indoor" in device.status_range
    assert "temp_indoor" in device.status_range
