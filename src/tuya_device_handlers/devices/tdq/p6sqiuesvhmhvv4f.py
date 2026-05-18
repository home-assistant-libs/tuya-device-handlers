"""Quirk for Contact sensor (product_id p6sqiuesvhmhvv4f).

Tuya does not advertise any datapoints for this device.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="p6sqiuesvhmhvv4f")
    .override_category("mcs")
    .add_dpid_boolean(
        dpid=101,
        dpcode="doorcontact_state",
        dpmode=DPMode.READ,
    )
    .add_dpid_enum(
        dpid=102,
        dpcode="battery_state",
        dpmode=DPMode.READ,
        enum_range=["low", "middle", "high"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
