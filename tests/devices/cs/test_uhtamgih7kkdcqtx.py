"""Test device-level quirk initialisation for CS devices."""

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_dehumidifier_remaps_humidity_and_temperature(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test DH-24 Nexi ION UV Wifi remaps custom DP codes."""
    device = create_device("cs_uhtamgih7kkdcqtx.json")

    definitions = get_sensor_default_definitions(device)
    assert "humidity_indoor" not in definitions
    assert "temp_indoor" not in definitions

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert "humidity_indoor" in definitions
    assert "temp_indoor" in definitions
