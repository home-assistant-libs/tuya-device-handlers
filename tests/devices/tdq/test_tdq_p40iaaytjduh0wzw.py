"""Test device-level quirk for 2CH Wi-Fi Smart Energy Monitor (p40iaaytjduh0wzw)."""

from tuya_sharing import Manager

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_adds_channel2_dps(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk adds Channel 2 datapoints (cur_current2, cur_power2, etc.)."""
    device = create_device("tdq_p40iaaytjduh0wzw.json")

    # Before quirk
    assert device.category == "tdq"
    assert "cur_current2" not in device.status_range
    assert "cur_power2" not in device.status_range
    assert "cur_voltage2" not in device.status_range
    assert "add_ele2" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    # After quirk
    assert "cur_current2" in device.status_range
    assert "cur_power2" in device.status_range
    assert "cur_voltage2" in device.status_range
    assert "add_ele2" in device.status_range


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk exposes Channel 2 sensors."""
    device = create_device("tdq_p40iaaytjduh0wzw.json")

    before = get_sensor_default_definitions(device)
    assert "cur_current2" not in before
    assert "cur_power2" not in before
    assert "cur_voltage2" not in before
    assert "add_ele2" not in before

    filled_quirks_registry.initialise_device_quirk(device)

    after = get_sensor_default_definitions(device)
    assert "cur_current2" in after
    assert "cur_power2" in after
    assert "cur_voltage2" in after
    assert "add_ele2" in after


def test_channel2_status_updates(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check Channel 2 values update via MQTT."""
    device = create_device("tdq_p40iaaytjduh0wzw.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    # Simulate Channel 2 power update (dpId 19 in the quirk mapping)
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 19, "t": 1752456620499, "value": 1250}],
    )
    assert device.status.get("cur_power2") == 1250

    # Simulate Channel 2 current update (dpId 18)
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 18, "t": 1752456620499, "value": 520}],
    )
    assert device.status.get("cur_current2") == 520

    # Simulate Channel 2 energy update (dpId 17)
    mock_manager._on_device_report(
        device.id,
        [{"dpId": 17, "t": 1752456620499, "value": 3400}],
    )
    assert device.status.get("add_ele2") == 3400
