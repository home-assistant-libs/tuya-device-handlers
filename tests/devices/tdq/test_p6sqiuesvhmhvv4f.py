"""Test device-level quirk initialisation."""

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
    """Quirk overrides the category and registers the contact datapoints."""
    device = create_device("tdq_p6sqiuesvhmhvv4f.json")
    assert device.category == "tdq"
    assert "doorcontact_state" not in device.status_range
    assert "battery_state" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "mcs"
    assert "doorcontact_state" in device.status_range
    assert "battery_state" in device.status_range


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk exposes the contact binary sensor and the battery sensor."""
    device = create_device("tdq_p6sqiuesvhmhvv4f.json")
    assert "doorcontact_state" not in get_binary_sensor_default_definitions(
        device
    )
    assert "battery_state" not in get_sensor_default_definitions(device)

    filled_quirks_registry.initialise_device_quirk(device)

    assert "doorcontact_state" in get_binary_sensor_default_definitions(device)
    assert "battery_state" in get_sensor_default_definitions(device)


def test_mqtt(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check local strategy handling."""
    device = create_device("tdq_p6sqiuesvhmhvv4f.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "mcs"
    assert "doorcontact_state" not in device.status

    # Trigger mqtt updates
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 101, "t": 1752456620499, "value": False}],
    )
    assert device.status["doorcontact_state"] is False

    mock_manager._on_device_report(
        device.id,
        [{"dpId": 101, "t": 1752456620499, "value": True}],
    )
    assert device.status["doorcontact_state"] is True
