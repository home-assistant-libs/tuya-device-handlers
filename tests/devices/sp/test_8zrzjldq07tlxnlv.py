"""Test device-level quirk initialisation."""

from unittest.mock import patch

from tuya_sharing import Manager

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry

_FEEDER_DPCODES = {
    238: "battery_status",
    239: "food_storage_status",
    240: "feed_block_status",
    241: "feed_stuck_status",
    243: "manual_feed_report",
    244: "auto_feed_report",
    246: "feed_report",
}


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk adds the feeder datapoints and keeps the camera ones."""
    device = create_device("sp_8zrzjldq07tlxnlv.json")
    for dpcode in _FEEDER_DPCODES.values():
        assert dpcode not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "sp"
    for dpid, dpcode in _FEEDER_DPCODES.items():
        assert dpcode in device.status_range
        assert dpcode not in device.function
        assert device.local_strategy[dpid]["status_code"] == dpcode
    assert device.status_range["food_storage_status"].values == (
        '{"range": ["full", "less", "lack"]}'
    )
    assert device.status_range["feed_report"].report_type == "sum"
    # Camera datapoints are left untouched
    assert "basic_nightvision" in device.function
    assert device.local_strategy[101]["status_code"] == "basic_indicator"


def test_mqtt(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Feeder reports reach the device status once the quirk is applied."""
    device = create_device("sp_8zrzjldq07tlxnlv.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    assert "feed_report" not in device.status

    # A 1-portion manual feed, as reported by a real device
    mock_manager._on_device_report(
        device.id,
        [
            {"dpId": 240, "t": 1793007330000, "value": False},
            {"dpId": 241, "t": 1793007330000, "value": False},
            {"dpId": 243, "t": 1793007330000, "value": 1},
            {"dpId": 246, "t": 1793007330000, "value": 1},
        ],
    )
    assert device.status["feed_block_status"] is False
    assert device.status["feed_stuck_status"] is False
    assert device.status["manual_feed_report"] == 1
    assert device.status["feed_report"] == 1

    mock_manager._on_device_report(
        device.id,
        [{"dpId": 239, "t": 1793007400000, "value": "less"}],
    )
    assert device.status["food_storage_status"] == "less"


def test_mqtt_without_quirk(mock_manager: Manager) -> None:
    """Without the quirk, feeder reports are dropped."""
    device = create_device("sp_8zrzjldq07tlxnlv.json")
    mock_manager.device_map[device.id] = device

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        TUYA_QUIRKS_REGISTRY.initialise_device_quirk(device)

    mock_manager._on_device_report(
        device.id,
        [{"dpId": 246, "t": 1793007330000, "value": 1}],
    )
    assert "feed_report" not in device.status
