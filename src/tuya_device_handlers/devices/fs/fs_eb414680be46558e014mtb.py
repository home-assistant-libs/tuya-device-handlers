from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

# Define the structured quirk using the fluent builder pattern
device_quirk = (
    DeviceQuirk()
    .applies_to(product_id="eb414680be46558e014mtb")
    .override_category("fs")
    # DP 1: Power Toggle (Read + Write)
    .add_dpid_boolean(dpid=1, dpcode="switch", dpmode=DPMode.READ | DPMode.WRITE)
    # DP 2: Wind Mode Options (Read + Write)
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["normal", "nature", "sleep"],
    )
    # DP 3: Integer Speed Scaling (Read + Write)
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
    .add_dpid_boolean(dpid=5, dpcode="switch_horizontal", dpmode=DPMode.READ | DPMode.WRITE)
    # DP 13: Read-only Manufacturer Flag (Read Only)
    .add_dpid_boolean(dpid=13, dpcode="status", dpmode=DPMode.READ)
    # DP 22: Sleep Timer Options (Read + Write)
    .add_dpid_enum(
        dpid=22,
        dpcode="countdown",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["cancel", "1h", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "10h", "11h", "12h"],
    )
)

# Explicitly invoke their custom registration workflow targeting the global handler registry
device_quirk.register(TUYA_QUIRKS_REGISTRY)
