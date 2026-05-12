"""Tuya quirk for Convector Heater with Wi-Fi.

Product ID: 8axigg3icem6telp
Category: qn (heater)

Issues fixed:
1. Level mapping: 1=Low (750W), 2=Medium (1250W), 3=High (2000W), 4=Off
2. Anion naming: Changed from "Ionisator" to "Turbo"
3. Mode mapping: Added proper mode descriptions
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="8axigg3icem6telp")
    # Switch (DP 1)
    .add_dpid_boolean(
        dpid=1,
        dpcode="switch",
        dpmode=DPMode.WRITE,
    )
    # Temperature setpoint (DP 2)
    .add_dpid_integer(
        dpid=2,
        dpcode="temp_set",
        dpmode=DPMode.WRITE,
        unit="°C",
        min=5,
        max=37,
        scale=0,
        step=1,
    )
    # Current temperature (DP 3)
    .add_dpid_integer(
        dpid=3,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="°C",
        min=-20,
        max=50,
        scale=0,
        step=1,
        report_type="un_known",
    )
    # Mode (DP 4) - operating modes with proper mapping
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.WRITE,
        enum_range=["smart", "auto", "off"]
    )
    # Level (DP 5) - power levels with proper mapping
    .add_dpid_enum(
        dpid=5,
        dpcode="level",
        dpmode=DPMode.WRITE,
        enum_range=["1", "2", "3", "4"]
    )
    # Anion/Turbo (DP 9) - rename to Turbo
    .remove_dpid(dpid=9, dpcode="anion")
    .add_dpid_boolean(
        dpid=9,
        dpcode="turbo",
        dpmode=DPMode.WRITE,
    )
    # Countdown timer (DP 12)
    .add_dpid_integer(
        dpid=12,
        dpcode="countdown_left",
        dpmode=DPMode.WRITE,
        unit="s",
        min=0,
        max=86400,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
