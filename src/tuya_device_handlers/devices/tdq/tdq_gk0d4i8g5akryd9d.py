"""Quirk for Motion Sensor (product_id gk0d4i8g5akryd9d).

Tuya does not advertise any datapoints for this device.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="gk0d4i8g5akryd9d")
    .override_category("pir")
    .add_dpid_enum(
        dpid=101,
        dpcode="pir",
        dpmode=DPMode.READ,
        enum_range=["pir", "none"],
    )
    .add_dpid_enum(
        dpid=102,
        dpcode="battery_state",
        dpmode=DPMode.READ,
        enum_range=["low", "middle", "high"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
