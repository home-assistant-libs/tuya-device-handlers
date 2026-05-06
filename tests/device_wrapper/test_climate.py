"""Test DeviceWrapper classes."""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.climate import (
    DefaultHVACModeWrapper,
    DefaultPresetModeWrapper,
    SwingModeCompositeWrapper,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaClimateHVACMode,
    TuyaClimateSwingMode,
)

from . import inject_dpcode


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
    """Test reading swing mode from device status."""
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
    """Test swing mode returns None when no dpcode is available."""
    wrapper = SwingModeCompositeWrapper.find_dpcode(mock_device)

    assert wrapper is None


@pytest.mark.parametrize(
    ("sample", "action", "expected"),
    [
        (
            "swing_only",
            TuyaClimateSwingMode.ON,
            [{"code": "swing", "value": True}],
        ),
        (
            "swing_only",
            TuyaClimateSwingMode.OFF,
            [{"code": "swing", "value": False}],
        ),
        (
            "horizontal_only",
            TuyaClimateSwingMode.HORIZONTAL,
            [{"code": "switch_horizontal", "value": True}],
        ),
        (
            "horizontal_only",
            TuyaClimateSwingMode.OFF,
            [{"code": "switch_horizontal", "value": False}],
        ),
        (
            "vertical_only",
            TuyaClimateSwingMode.VERTICAL,
            [{"code": "switch_vertical", "value": True}],
        ),
        (
            "vertical_only",
            TuyaClimateSwingMode.OFF,
            [{"code": "switch_vertical", "value": False}],
        ),
        (
            "both",
            TuyaClimateSwingMode.BOTH,
            [
                {"code": "switch_vertical", "value": True},
                {"code": "switch_horizontal", "value": True},
            ],
        ),
    ],
)
def test_swing_mode_action_command(
    sample: str,
    action: TuyaClimateSwingMode,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    if sample == "swing_only":
        inject_dpcode(mock_device, "swing", None, dptype="Boolean")
    if sample in {"horizontal_only", "both"}:
        inject_dpcode(mock_device, "switch_horizontal", None, dptype="Boolean")
    if sample in {"vertical_only", "both"}:
        inject_dpcode(mock_device, "switch_vertical", None, dptype="Boolean")
    wrapper = SwingModeCompositeWrapper.find_dpcode(mock_device)

    assert wrapper
    assert wrapper.get_update_commands(mock_device, action) == expected


@pytest.mark.parametrize(
    ("range", "status_updates", "expected_hvac_mode", "expected_preset"),
    [
        (
            '["cold", "hot", "wet", "wind", "auto"]',
            {"mode": "cold"},
            TuyaClimateHVACMode.COOL,
            None,
        ),
        (
            '["cold", "freeze", "hot", "wet", "wind", "auto"]',
            {"mode": "cold"},
            TuyaClimateHVACMode.COOL,
            "cold",
        ),
        (
            '["cold", "freeze", "hot", "wet", "wind", "auto"]',
            {"mode": "auto"},
            TuyaClimateHVACMode.HEAT_COOL,
            None,
        ),
        (
            '["cold", "freeze", "hot", "wet", "wind", "auto"]',
            {},
            None,
            None,
        ),
        (
            '["auto", "manual", "off"]',
            {"mode": "manual"},
            TuyaClimateHVACMode.HEAT_COOL,
            "manual",
        ),
    ],
)
def test_read_hvac_preset(
    range: str,
    status_updates: dict[str, Any],
    expected_hvac_mode: Any,
    expected_preset: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test reading HVAC mode and preset from device status."""
    inject_dpcode(
        mock_device,
        "mode",
        None,
        dptype="Enum",
        values=f'{{"range": {range}}}',
    )
    mock_device.status.update(status_updates)
    hvac_wrapper = DefaultHVACModeWrapper.find_dpcode(mock_device, "mode")
    preset_wrapper = DefaultPresetModeWrapper.find_dpcode(mock_device, "mode")

    assert hvac_wrapper and preset_wrapper
    assert hvac_wrapper.read_device_status(mock_device) == expected_hvac_mode
    assert preset_wrapper.read_device_status(mock_device) == expected_preset


@pytest.mark.parametrize(
    ("range", "action", "expected"),
    [
        (
            '["cold", "hot", "wet", "wind", "auto"]',
            TuyaClimateHVACMode.COOL,
            [{"code": "mode", "value": "cold"}],
        ),
        (
            '["cold", "hot", "wet", "wind", "auto"]',
            TuyaClimateHVACMode.HEAT,
            [{"code": "mode", "value": "hot"}],
        ),
    ],
)
def test_hvac_action_command(
    range: str,
    action: TuyaClimateHVACMode,
    expected: list[dict[str, Any]],
    mock_device: CustomerDevice,
) -> None:
    """Test get_update_commands."""
    inject_dpcode(
        mock_device,
        "mode",
        None,
        dptype="Enum",
        values=f'{{"range": {range}}}',
    )
    wrapper = DefaultHVACModeWrapper.find_dpcode(mock_device, "mode")

    assert wrapper
    assert wrapper.get_update_commands(mock_device, action) == expected
