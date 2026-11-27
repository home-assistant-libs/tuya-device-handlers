"""Tests for WiFi PIR Motion & T&H Sensor (m1ggi8iay3aa8g9u) quirk."""

from unittest.mock import patch

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry
from tuya_device_handlers.type_information import IntegerTypeInformation


def test_quirk_adds_humidity_and_illuminance(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Verify humidity and illuminance datapoints with and without quirk."""
    device = create_device("pir_m1ggi8iay3aa8g9u.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        assert "humidity_value" not in device.status_range
        assert "illuminance_value" not in device.status_range
        assert (
            IntegerTypeInformation.find_dpcode(device, "humidity_value") is None
        )
        assert (
            IntegerTypeInformation.find_dpcode(device, "illuminance_value")
            is None
        )

    filled_quirks_registry.initialise_device_quirk(device)

    assert "humidity_value" in device.status_range
    assert "illuminance_value" in device.status_range
    assert device.status_range["humidity_value"].values == (
        '{"unit": "%", "min": 0, "max": 100, "scale": 0, "step": 1}'
    )
    assert device.status_range["illuminance_value"].values == (
        '{"unit": "lx", "min": 0, "max": 100000, "scale": 0, "step": 1}'
    )

    humidity_info = IntegerTypeInformation.find_dpcode(device, "humidity_value")
    assert humidity_info is not None
    assert humidity_info.read_device_value(device) == 50

    illuminance_info = IntegerTypeInformation.find_dpcode(
        device, "illuminance_value"
    )
    assert illuminance_info is not None
    assert illuminance_info.read_device_value(device) == 2979
