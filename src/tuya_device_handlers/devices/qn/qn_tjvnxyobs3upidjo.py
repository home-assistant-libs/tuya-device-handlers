"""Quirk for Heater (tjvnxyobs3upidjo).

The cloud only reports the "eco" mode, so the device cannot be turned off.
Add the missing "off" value to the mode enum range.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="tjvnxyobs3upidjo")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["eco", "off"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
