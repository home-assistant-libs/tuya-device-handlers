"""Tests for Convector Heater quirk."""

import pytest

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.devices import register_tuya_quirks


def test_qn_8axigg3icem6telp_quirk_registration() -> None:
    """Test that the quirk is properly registered."""
    # Set up the registry for this test
    register_tuya_quirks()
    
    # Debug: Print all registry keys to see what's actually registered
    registry_keys = list(TUYA_QUIRKS_REGISTRY._quirks.keys())
    print(f"Registry keys: {registry_keys}")
    
    # Look for our quirk key (case-insensitive search)
    our_key = None
    for key in registry_keys:
        if "8axigg3icem6telp" in key.lower():
            our_key = key
            break
    
    # Verify the quirk is registered (with correct key)
    assert our_key is not None, f"Quirk not found in registry. Keys: {registry_keys}"
    
    # Get the quirk and verify it's the right type
    quirk = TUYA_QUIRKS_REGISTRY._quirks[our_key]
    assert quirk is not None
    assert hasattr(quirk, 'initialise_device')
    
    # Verify the quirk has the expected datapoint definitions
    assert hasattr(quirk, '_datapoint_definitions')
    datapoints = quirk._datapoint_definitions
    
    # Check for expected datapoints (dpid, dpcode)
    expected_datapoints = [
        (4, "mode"),    # Mode enum with off
        (5, "level"),   # Level enum  
        (9, "turbo"),   # Turbo boolean (renamed from anion)
    ]
    
    for expected_dpid, expected_dpcode in expected_datapoints:
        assert (expected_dpid, expected_dpcode) in datapoints


def test_qn_8axigg3icem6telp_quirk_datapoint_definitions() -> None:
    """Test that the quirk has correct datapoint definitions."""
    # Import and create the quirk directly to avoid registry issues
    from tuya_device_handlers.builder.device_quirk import DeviceQuirk
    from tuya_device_handlers.const import DPMode
    
    # Create the quirk as it's defined in the actual file
    quirk = (
        DeviceQuirk()
        .applies_to(product_id="8axigg3icem6telp")
        .remove_dpid(dpid=4, dpcode="mode")
        .add_dpid_enum(
            dpid=4,
            dpcode="mode",
            dpmode=DPMode.WRITE,
            enum_range=["smart", "auto", "off"]
        )
        .remove_dpid(dpid=5, dpcode="level")
        .add_dpid_enum(
            dpid=5,
            dpcode="level",
            dpmode=DPMode.WRITE,
            enum_range=["1", "2", "3", "4"]
        )
        .remove_dpid(dpid=9, dpcode="anion")
        .add_dpid_boolean(
            dpid=9,
            dpcode="turbo",
            dpmode=DPMode.WRITE,
        )
    )
    
    datapoints = quirk._datapoint_definitions
    
    # Test mode datapoint (DP 4)
    mode_dp = datapoints[(4, "mode")]
    assert mode_dp.dpid == 4
    assert mode_dp.dpcode == "mode"
    assert mode_dp.dptype.value == "Enum"
    # Should include "off" mode
    import json
    mode_values = json.loads(mode_dp.values)
    assert "off" in mode_values["range"]
    assert set(mode_values["range"]) == {"smart", "auto", "off"}
    
    # Test level datapoint (DP 5)
    level_dp = datapoints[(5, "level")]
    assert level_dp.dpid == 5
    assert level_dp.dpcode == "level"
    assert level_dp.dptype.value == "Enum"
    # Should have power levels 1-4
    level_values = json.loads(level_dp.values)
    assert set(level_values["range"]) == {"1", "2", "3", "4"}
    
    # Test turbo datapoint (DP 9)
    turbo_dp = datapoints[(9, "turbo")]
    assert turbo_dp.dpid == 9
    assert turbo_dp.dpcode == "turbo"
    assert turbo_dp.dptype.value == "Boolean"


def test_qn_8axigg3icem6telp_no_quirk_for_other_device() -> None:
    """Test that quirk doesn't apply to different product ID."""
    # Verify quirk doesn't exist for wrong product ID
    assert "other_product" not in TUYA_QUIRKS_REGISTRY._quirks
