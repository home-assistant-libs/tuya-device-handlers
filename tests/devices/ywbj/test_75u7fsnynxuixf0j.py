"""Test device-level quirk for Wi-Fi Smoke Detector.

with Temp & Humidity (75u7fsnynxuixf0j).
"""

from tuya_sharing import Manager

from tests import create_device
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


def test_smoke_detector_status_updates(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check temperature, humidity, and smoke status values update via MQTT."""
    device = create_device("ywbj_75u7fsnynxuixf0j.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    # Simulate Temperature update (dpId 23)-device.status holds raw value (189)
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 23, "t": 1752456620499, "value": 189}],
    )
    assert device.status.get("temp_current") == 189

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
