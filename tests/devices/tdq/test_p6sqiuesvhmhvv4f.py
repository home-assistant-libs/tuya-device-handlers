"""Test device-level quirk initialisation."""

from tuya_sharing import Manager

from tests import create_device
from tuya_device_handlers.definition.binary_sensor import (
    get_default_definition as get_binary_sensor_definition,
)
from tuya_device_handlers.definition.sensor import (
    get_default_definition as get_sensor_definition,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_default_definition(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing datapoints."""
    device = create_device("tdq_p6sqiuesvhmhvv4f.json")
    assert device.category == "tdq"
    assert get_binary_sensor_definition(device, "doorcontact_state") is None
    assert get_sensor_definition(device, "battery_state") is None

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "mcs"
    assert get_binary_sensor_definition(device, "doorcontact_state") is not None
    assert get_sensor_definition(device, "battery_state") is not None


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
