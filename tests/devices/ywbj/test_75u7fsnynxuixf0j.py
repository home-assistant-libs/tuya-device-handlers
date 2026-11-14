"""Test device-level quirk for Wi-Fi Smoke Detector with Temp & Humidity (75u7fsnynxuixf0j)."""

from tuya_sharing import Manager

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_adds_smoke_detector_dps(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk adds temperature (dp 23) and humidity (dp 24) datapoints."""
    device = create_device("ywbj_75u7fsnynxuixf0j.json")

    # Before quirk initialization
    assert device.category == "ywbj"
    assert "temp_current" not in device.status_range
    assert "humidity_value" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    # After quirk initialization
    assert "temp_current" in device.status_range
    assert "humidity_value" in device.status_range


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk exposes temperature and humidity sensors."""
    device = create_device("ywbj_75u7fsnynxuixf0j.json")

    before = get_sensor_default_definitions(device)
    assert "temp_current" not in before
    assert "humidity_value" not in before

    filled_quirks_registry.initialise_device_quirk(device)

    after = get_sensor_default_definitions(device)
    assert "temp_current" in after
    assert "humidity_value" in after


def test_smoke_detector_status_updates(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check temperature, humidity, and smoke status values update via MQTT."""
    device = create_device("ywbj_75u7fsnynxuixf0j.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    # Simulate Temperature update (dpId 23)
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 23, "t": 1752456620499, "value": 189}],
    )
    assert device.status.get("temp_current") == 18.9

    # Simulate Humidity update (dpId 24)
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 24, "t": 1752456620499, "value": 64}],
    )
    assert device.status.get("humidity_value") == 64

    # Simulate Smoke Alarm status update (dpId 1)
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 1, "t": 1752456620499, "value": "alarm"}],
    )
    assert device.status.get("smoke_sensor_status") == "alarm"
