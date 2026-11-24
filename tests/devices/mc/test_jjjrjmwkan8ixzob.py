"""Tests for the jjjrjmwkan8ixzob door sensor quirk.

The cloud's local strategy converts `doorcontact_state` reports to the
strings "true"/"false" instead of booleans.

See https://github.com/home-assistant/core/issues/193365.
"""

from unittest.mock import patch

from tuya_sharing import Manager

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def _report_door(manager: Manager, device_id: str, value: str) -> None:
    manager._on_device_report(
        device_id, [{"dpId": 1, "t": 1795148949000, "value": value}]
    )


def test_without_quirk_reports_strings(mock_manager: Manager) -> None:
    """Without the quirk, reports are stored as "true"/"false" strings."""
    device = create_device("mc_jjjrjmwkan8ixzob.json")
    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        TUYA_QUIRKS_REGISTRY.initialise_device_quirk(device)
    mock_manager.device_map[device.id] = device

    # The fixture was downloaded after such a report.
    assert device.status["doorcontact_state"] == "false"

    _report_door(mock_manager, device.id, "opened")
    assert device.status["doorcontact_state"] == "true"

    _report_door(mock_manager, device.id, "closed")
    assert device.status["doorcontact_state"] == "false"


def test_quirk_sets_boolean_strategy(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The quirk maps opened/closed to booleans in the local strategy."""
    device = create_device("mc_jjjrjmwkan8ixzob.json")

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.local_strategy[1]["config_item"]["enumMappingMap"] == {
        "opened": {"value": True},
        "closed": {"value": False},
    }
    # Only raw opened/closed values are mapped: the cached "false" string
    # was already converted by the original strategy, so it is left as is.
    assert device.status["doorcontact_state"] == "false"


def test_quirk_reports_booleans(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """With the quirk, reports are stored as booleans."""
    device = create_device("mc_jjjrjmwkan8ixzob.json")
    filled_quirks_registry.initialise_device_quirk(device)
    mock_manager.device_map[device.id] = device

    _report_door(mock_manager, device.id, "opened")
    assert device.status["doorcontact_state"] is True

    _report_door(mock_manager, device.id, "closed")
    assert device.status["doorcontact_state"] is False
