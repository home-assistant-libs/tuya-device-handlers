"""Quirk for Warmtec T510 thermostat (product_id ucf09xuve67adcp4).

DP 2 (``mode``) is missing values: comfort, holiday (only has auto, eco)
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="ucf09xuve67adcp4",
        manufacturer="Warmtec",
        model="Thermostat",
        model_id="T510",
    )
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "comfort", "eco", "holiday"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
