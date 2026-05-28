"""Quirk for R11 Smart Wifi Thermostat (product_id if6pqia2gbtvqa6l).

DP 2 (``mode``) is missing the expected ``home`` value for the enum
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="if6pqia2gbtvqa6l")
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "home"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
