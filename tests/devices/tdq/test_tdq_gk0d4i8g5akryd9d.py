"""Test device-level quirk initialization."""

from tuya_sharing import Manager

from tests import create_device
from tests.integration_helpers.binary_sensor import (
    get_binary_sensor_default_definitions,
)
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk overrides the category and registers the motion datapoints."""
    device = create_device("tdq_gk0d4i8g5akryd9d.json")
    assert device.category == "tdq"
    assert "pir" not in device.status_range
    assert "battery_state" not in device.status_range
    assert "pir" not in device.status

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "pir"
    assert "pir" in device.status_range
    assert "battery_state" in device.status_range
    assert "pir" not in device.status


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk exposes the motion binary sensor and the battery sensor."""
    device = create_device("tdq_gk0d4i8g5akryd9d.json")
    assert "pir" not in get_binary_sensor_default_definitions(device)
    assert "battery_state" not in get_sensor_default_definitions(device)

    filled_quirks_registry.initialise_device_quirk(device)

    assert "pir" in get_binary_sensor_default_definitions(device)
    assert "battery_state" in get_sensor_default_definitions(device)


def test_motion_status_updates(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check motion detection updates via MQTT."""
    device = create_device("tdq_gk0d4i8g5akryd9d.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    assert "pir" not in device.status

    # Simulate motion detected via MQTT
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 101, "t": 1752456620499, "value": "pir"}],
    )
    assert device.status["pir"] == "pir"

    # Simulate motion cleared via MQTT
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 101, "t": 1752456620499, "value": "none"}],
    )
    assert device.status["pir"] == "none"


def test_battery_status_updates(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check battery state updates via MQTT."""
    device = create_device("tdq_gk0d4i8g5akryd9d.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    assert "pir" not in device.status

    # Simulate battery state update via MQTT
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 102, "t": 1752456620499, "value": "low"}],
    )
    assert device.status["battery_state"] == "low"
