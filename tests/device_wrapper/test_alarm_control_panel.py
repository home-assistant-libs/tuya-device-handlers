"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.device_wrapper.alarm_control_panel import (
    AlarmActionWrapper,
    AlarmChangedByWrapper,
    AlarmStateWrapper,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaAlarmControlPanelAction,
    TuyaAlarmControlPanelState,
)

from . import inject_dpcode

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


def _inject_default_alarm_codes(mock_device: CustomerDevice) -> None:
    inject_dpcode(mock_device, "alarm_msg", "**REDACTED**", dptype="Raw")
    inject_dpcode(
        mock_device,
        "master_mode",
        "disarmed",
        dptype="Enum",
        values='{"range": ["disarmed", "arm", "home", "sos"]}',
    )
    inject_dpcode(
        mock_device,
        "master_state",
        "normal",
        dptype="Enum",
        values='{"range": ["normal", "alarm"]}',
    )


@pytest.mark.parametrize(
    ("status_updates", "expected_state", "expected_changed_by"),
    [
        (
            {"master_mode": "disarmed"},
            TuyaAlarmControlPanelState.DISARMED,
            None,
        ),
        (
            {"master_mode": "arm"},
            TuyaAlarmControlPanelState.ARMED_AWAY,
            None,
        ),
        (
            {"master_mode": "home"},
            TuyaAlarmControlPanelState.ARMED_HOME,
            None,
        ),
        (
            {"master_mode": "sos"},
            TuyaAlarmControlPanelState.TRIGGERED,
            None,
        ),
        (
            {
                "master_mode": "home",
                "master_state": "alarm",
                # "Test Sensor" in UTF-16BE
                "alarm_msg": "AFQAZQBzAHQAIABTAGUAbgBzAG8Acg==",
            },
            TuyaAlarmControlPanelState.TRIGGERED,
            "Test Sensor",
        ),
        (
            {
                "master_mode": "home",
                "master_state": "alarm",
                # "Sensor Low Battery Test Sensor" in UTF-16BE
                "alarm_msg": "AFMAZQBuAHMAbwByACAATABvAHcAIABCAGEAdAB0AGUAcgB5ACAAVABlAHMAdAAgAFMAZQBuAHMAbwBy",
            },
            TuyaAlarmControlPanelState.ARMED_HOME,
            "Sensor Low Battery Test Sensor",
        ),
    ],
)
def test_read_device_status(
    status_updates: dict[str, Any],
    expected_state: TuyaAlarmControlPanelState,
    expected_changed_by: str | None,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    _inject_default_alarm_codes(mock_device)
    mock_device.status.update(status_updates)
    changed_by_wrapper = AlarmChangedByWrapper.find_dpcode(
        mock_device, "alarm_msg"
    )
    state_wrapper = AlarmStateWrapper.find_dpcode(mock_device, "master_mode")

    assert state_wrapper
    assert state_wrapper.read_device_status(mock_device) == expected_state
    assert changed_by_wrapper
    assert (
        changed_by_wrapper.read_device_status(mock_device)
        == expected_changed_by
    )

    # All wrappers return None if status is None
    for dpcode in ["alarm_msg", "master_mode", "master_state"]:
        mock_device.status[dpcode] = None
    assert state_wrapper.read_device_status(mock_device) is None

    # All wrappers return None if status is missing
    for dpcode in ["alarm_msg", "master_mode", "master_state"]:
        mock_device.status.pop(dpcode)
    assert state_wrapper.read_device_status(mock_device) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            TuyaAlarmControlPanelAction.ARM_AWAY,
            [{"code": "master_mode", "value": "arm"}],
        ),
        (
            TuyaAlarmControlPanelAction.ARM_HOME,
            [{"code": "master_mode", "value": "home"}],
        ),
        (
            TuyaAlarmControlPanelAction.DISARM,
            [{"code": "master_mode", "value": "disarmed"}],
        ),
        (
            TuyaAlarmControlPanelAction.TRIGGER,
            [{"code": "master_mode", "value": "sos"}],
        ),
    ],
)
def test_get_update_commands(
    value: TuyaAlarmControlPanelAction,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    _inject_default_alarm_codes(mock_device)
    wrapper = AlarmActionWrapper.find_dpcode(mock_device, "master_mode")

    assert wrapper
    assert wrapper.get_update_commands(mock_device, value) == expected


def test_invalid_update_commands(
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    _inject_default_alarm_codes(mock_device)
    wrapper = AlarmActionWrapper.find_dpcode(mock_device, "master_mode")

    assert wrapper
    with pytest.raises(
        ValueError, match="Unsupported value 12 for master_mode"
    ):
        assert wrapper.get_update_commands(mock_device, "12")  # type: ignore[arg-type]
