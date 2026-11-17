"""Quirk for Panel Heater (apnfmkj7hm0e3hfo).

The cloud only reports the "eco" mode, but the device also reports
"comfor" (comfort). Add the missing value to the mode enum range.

See https://github.com/home-assistant-libs/tuya-device-handlers/issues/443.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="apnfmkj7hm0e3hfo")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["comfor", "eco"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
