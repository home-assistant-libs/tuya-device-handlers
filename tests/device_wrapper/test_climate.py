"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.device_wrapper.climate import (
    SwingModeCompositeWrapper,
)
from tuya_device_handlers.helpers.homeassistant import TuyaClimateSwingMode

from . import inject_dpcode

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


@pytest.mark.parametrize(
    (
        "sample",
        "status_updates",
        "expected_device_status",
    ),
    [
        ("swing_only", {"swing": True}, TuyaClimateSwingMode.ON),
        ("swing_only", {"swing": False}, TuyaClimateSwingMode.OFF),
        (
            "horizontal_only",
            {"switch_horizontal": True},
            TuyaClimateSwingMode.HORIZONTAL,
        ),
        (
            "horizontal_only",
            {"switch_horizontal": False},
            TuyaClimateSwingMode.OFF,
        ),
        (
            "vertical_only",
            {"switch_vertical": True},
            TuyaClimateSwingMode.VERTICAL,
        ),
        (
            "vertical_only",
            {"switch_vertical": False},
            TuyaClimateSwingMode.OFF,
        ),
        (
            "both",
            {"switch_horizontal": True, "switch_vertical": True},
            TuyaClimateSwingMode.BOTH,
        ),
    ],
)
def test_read_swing_mode(
    sample: str,
    status_updates: dict[str, Any],
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    if sample == "swing_only":
        inject_dpcode(mock_device, "swing", None, dptype="Boolean")
    if sample in {"horizontal_only", "both"}:
        inject_dpcode(mock_device, "switch_horizontal", None, dptype="Boolean")
    if sample in {"vertical_only", "both"}:
        inject_dpcode(mock_device, "switch_vertical", None, dptype="Boolean")
    mock_device.status.update(status_updates)
    wrapper = SwingModeCompositeWrapper.find_dpcode(mock_device)

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status


def test_swing_mode_unavailable(
    mock_device: CustomerDevice,
) -> None:
    wrapper = SwingModeCompositeWrapper.find_dpcode(mock_device)

    assert wrapper is None
