"""Quirk for Comfort Zone Tower Fan (CZTF423S)."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

# Define the structured quirk using the fluent builder pattern
device_quirk = (
    DeviceQuirk()
    .applies_to(product_id="eb414680be46558e014mtb")
    .override_category("fs")
    # DP 1: Power Toggle (Read + Write)
    .add_dpid_boolean(
        dpid=1, dpcode="switch", dpmode=DPMode.READ | DPMode.WRITE
    )
    # DP 2: Wind Mode Options (Read + Write)
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["normal", "nature", "sleep"],
    )
    # DP 3: Integer Speed Scaling (Read + Write)
    # Note: replaces auto-configured "fan_speed_percent"
    .remove_dpid(dpid=3, dpcode="fan_speed_percent")
    .add_dpid_integer(
        dpid=3,
        dpcode="speed",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="",
        min=1,
        max=5,
        scale=0,
        step=1,
    )
    # DP 5: Oscillation / Horizontal Swing (Read + Write)
    .add_dpid_boolean(
        dpid=5, dpcode="switch_horizontal", dpmode=DPMode.READ | DPMode.WRITE
    )
    # DP 13: Remove non-functional fan_beep
    .remove_dpid(dpid=13, dpcode="fan_beep")
    # DP 22: Sleep Timer Options (Read + Write)
    # Note: replaces auto-configured "countdown_set" with more options
    .remove_dpid(dpid=22, dpcode="countdown_set")
    .add_dpid_enum(
        dpid=22,
        dpcode="countdown",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=[
            "cancel",
            "1h",
            "2h",
            "3h",
            "4h",
            "5h",
            "6h",
            "7h",
            "8h",
            "9h",
            "10h",
            "11h",
            "12h",
        ],
    )
)

# Register quirk with global handler registry
device_quirk.register(TUYA_QUIRKS_REGISTRY)
