"""Test device-level quirk initialisation for CS devices."""

from tests import create_device
from tests.devices.sensor_helpers import (
    get_sensor_default_definitions,
    get_sensor_wrapper,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_dehumidifier_remaps_humidity_and_temperature(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test DH-24 Nexi ION UV Wifi remaps custom DP codes."""
    device = create_device("cs_uhtamgih7kkdcqtx.json")

    definitions = get_sensor_default_definitions(device)
    assert get_sensor_wrapper(definitions, "humidity_indoor") is None
    assert get_sensor_wrapper(definitions, "temp_indoor") is None

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert get_sensor_wrapper(definitions, "humidity_indoor") is not None
    assert get_sensor_wrapper(definitions, "temp_indoor") is not None
