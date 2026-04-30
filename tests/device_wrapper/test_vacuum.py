"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.vacuum import (
    VacuumActionWrapper,
    VacuumActivityWrapper,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaVacuumAction,
    TuyaVacuumActivity,
)

from . import inject_dpcode

try:
    from typeguard import suppress_type_checks  # ty: ignore[unresolved-import]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks: Any = nullcontext


@pytest.mark.parametrize(
    ("sample", "status_updates", "expected_device_status"),
    [
        (
            "status_wrapper",
            {},
            TuyaVacuumActivity.DOCKED,
        ),
        (
            "status_wrapper",
            {"status": "cleaning"},
            TuyaVacuumActivity.CLEANING,
        ),
        (
            "status_wrapper",
            {"status": "goto_charge"},
            TuyaVacuumActivity.RETURNING,
        ),
        (
            "pause_wrapper",
            {"pause": True},
            TuyaVacuumActivity.PAUSED,
        ),
        (
            "pause_wrapper",
            {"pause": False},
            None,
        ),
    ],
)
def test_read_device_status(
    sample: str,
    status_updates: dict[str, Any],
    expected_device_status: TuyaVacuumActivity,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    inject_dpcode(mock_device, "pause", False, dptype="Boolean")
    if sample == "status_wrapper":
        inject_dpcode(
            mock_device,
            "status",
            "charge_done",
            dptype="Enum",
            values='{"range": ["standby","zone_clean","part_clean","cleaning","paused","goto_pos","pos_arrived","pos_unarrive","goto_charge","charging","charge_done","sleep"]}',
        )

    mock_device.status.update(status_updates)
    wrapper = VacuumActivityWrapper.find_dpcode(mock_device)

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status


@pytest.mark.parametrize(
    ("sample", "action", "expected"),
    [
        (
            "wrapper_1",
            TuyaVacuumAction.RETURN_TO_BASE,
            [{"code": "mode", "value": "chargego"}],
        ),
        (
            "wrapper_1",
            TuyaVacuumAction.LOCATE,
            [{"code": "seek", "value": True}],
        ),
        (
            "wrapper_1",
            TuyaVacuumAction.START,
            [{"code": "power_go", "value": True}],
        ),
        (
            "wrapper_1",
            TuyaVacuumAction.STOP,
            [{"code": "power_go", "value": False}],
        ),
        (
            "wrapper_1",
            TuyaVacuumAction.PAUSE,
            [{"code": "power_go", "value": False}],
        ),
        (
            "wrapper_2",
            TuyaVacuumAction.RETURN_TO_BASE,
            [{"code": "switch_charge", "value": True}],
        ),
        (
            "wrapper_2",
            TuyaVacuumAction.LOCATE,
            [],
        ),
        (
            "wrapper_3",
            TuyaVacuumAction.RETURN_TO_BASE,
            [],
        ),
    ],
)
def test_vacuum_action_command(
    sample: str,
    action: TuyaVacuumAction,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    if sample == "wrapper_1":
        inject_dpcode(mock_device, "power", False, dptype="Boolean")
        inject_dpcode(mock_device, "seek", False, dptype="Boolean")
        inject_dpcode(
            mock_device,
            "mode",
            "chargego",
            dptype="Enum",
            values='{"range": ["random", "smart", "wall_follow", "chargego"]}',
        )
        inject_dpcode(mock_device, "power_go", False, dptype="Boolean")
    elif sample == "wrapper_2":
        inject_dpcode(mock_device, "switch_charge", False, dptype="Boolean")
        inject_dpcode(mock_device, "pause", False, dptype="Boolean")

    wrapper = VacuumActionWrapper.find_dpcode(mock_device)

    assert wrapper
    assert wrapper.get_update_commands(mock_device, action) == expected


def test_find_dpcode_failure(
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    wrapper = VacuumActivityWrapper.find_dpcode(mock_device)

    assert wrapper is None
