"""Test device-level quirk initialisation for BH devices."""

import json

from tuya_sharing import Manager

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_kettle_maps_cached_work_type(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test xo5wnj56ip8haw1s stores the catalog value for work_type."""
    device = create_device("bh_xo5wnj56ip8haw1s.json")

    assert device.status["work_type"] == "heating_quick"

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.status["work_type"] == "boiling_quick"
    assert json.loads(device.status_range["work_type"].values) == {
        "range": ["boiling_quick"]
    }
    assert device.local_strategy[9]["config_item"]["enumMappingMap"] == {
        "heating_quick": {"value": "boiling_quick"},
        "boiling_quick": {"value": "boiling_quick"},
    }


def test_kettle_maps_reported_work_type(
    filled_quirks_registry: QuirksRegistry,
    mock_manager: Manager,
) -> None:
    """Test a report of heating_quick is stored as boiling_quick."""
    device = create_device("bh_xo5wnj56ip8haw1s.json")
    filled_quirks_registry.initialise_device_quirk(device)
    device.status["work_type"] = "heating_quick"
    mock_manager.device_map[device.id] = device

    mock_manager._on_device_report(
        device.id, [{"dpId": 9, "t": 1752456620499, "value": "heating_quick"}]
    )

    assert device.status["work_type"] == "boiling_quick"
