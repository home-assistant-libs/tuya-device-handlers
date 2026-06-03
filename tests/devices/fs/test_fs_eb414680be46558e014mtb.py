"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """CZTF423S tower fan has non-standard DP code names.

    Auto-configuration maps them as fan_speed_percent and countdown_set.
    The quirk normalizes these to standard names: speed and countdown.
    It also expands the mode range to include "normal".
    """
    device = create_device("fs_eb414680be46558e014mtb.json")

    # BEFORE quirk: verify non-standard DP code names are present
    assert "fan_speed_percent" in device.function
    assert "countdown_set" in device.function
    assert "fan_beep" in device.function
    # Standard names not yet present
    assert "speed" not in device.function
    assert "countdown" not in device.function
    assert "status" not in device.function
    # Mode range is missing "normal"
    mode_func = device.function.get("mode")
    assert mode_func is not None
    assert '"range":["nature","sleep"]' in mode_func.values

    # APPLY quirk
    filled_quirks_registry.initialise_device_quirk(device)

    # AFTER quirk: verify standard DP code names are now present
    assert "speed" in device.function
    assert "countdown" in device.function
    # Old non-standard names should be removed
    assert "fan_speed_percent" not in device.function
    assert "countdown_set" not in device.function
    assert "fan_beep" not in device.function
    # Verify all DPs are in status_range
    assert "switch" in device.status_range
    assert "mode" in device.status_range
    assert "speed" in device.status_range
    assert "switch_horizontal" in device.status_range
    assert "countdown" in device.status_range
    # Mode range should now include "normal"
    mode_range = device.status_range.get("mode")
    assert mode_range is not None
    assert '"range": ["normal", "nature", "sleep"]' in mode_range.values
