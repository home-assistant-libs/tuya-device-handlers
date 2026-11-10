"""Test device-level quirk initialisation."""

from tuya_sharing import Manager

from tests import create_device
from tests.integration_helpers.binary_sensor import (
    get_binary_sensor_default_definitions,
)
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_adds_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk registers the door, tamper and battery datapoints."""
    device = create_device("mcs_KajlwMlIaQUARNpb.json")
    assert device.status_range == {}

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "mcs"
    assert set(device.status_range) == {
        "doorcontact_state",
        "temper_alarm",
        "battery_percentage",
    }
    assert device.function == {}


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk exposes door and tamper binary sensors and a battery sensor."""
    device = create_device("mcs_KajlwMlIaQUARNpb.json")
    assert get_binary_sensor_default_definitions(device) == {}
    assert get_sensor_default_definitions(device) == {}

    filled_quirks_registry.initialise_device_quirk(device)

    assert {"doorcontact_state", "temper_alarm"} <= set(
        get_binary_sensor_default_definitions(device)
    )
    assert "battery_percentage" in get_sensor_default_definitions(device)


def test_mqtt(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check local strategy handling of MQTT reports."""
    device = create_device("mcs_KajlwMlIaQUARNpb.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    mock_manager._on_device_report(
        device.id,
        [
            {"dpId": 101, "t": 1794096541000, "value": True},
            {"dpId": 102, "t": 1794096541000, "value": False},
            {"dpId": 103, "t": 1794096541000, "value": 100},
        ],
    )
    assert device.status["doorcontact_state"] is True
    assert device.status["temper_alarm"] is False
    assert device.status["battery_percentage"] == 100

    mock_manager._on_device_report(
        device.id,
        [{"dpId": 101, "t": 1794096550000, "value": False}],
    )
    assert device.status["doorcontact_state"] is False
