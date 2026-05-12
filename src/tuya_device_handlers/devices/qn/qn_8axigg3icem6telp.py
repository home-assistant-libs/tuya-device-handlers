"""Tuya quirk for Convector Heater with Wi-Fi.

Product ID: 8axigg3icem6telp
Category: qn (heater)

Issues fixed:
1. Level mapping: 1=Low (750W), 2=Medium (1250W), 3=High (2000W), 4=Off
2. Anion naming: Changed from "Ionisator" to "Turbo" 
3. Mode mapping: Added "off" mode to existing smart/auto modes
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="8axigg3icem6telp")
    # Mode (DP 4) - add "off" mode to existing smart/auto modes
    .remove_dpid(dpid=4, dpcode="mode")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.WRITE,
        enum_range=["smart", "auto", "off"]
    )
    # Level (DP 5) - ensure proper power level mapping exists
    # Note: This datapoint already exists in the device, but we redefine it
    # to ensure the enum values are correctly handled by Home Assistant
    .remove_dpid(dpid=5, dpcode="level")
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
    .register(TUYA_QUIRKS_REGISTRY)
)
