"""Quirk for Eeese Otto dehumidifier. Adds Tank Full information."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="ma3oq4onxxwg91ky",
    )
    .add_dpid_bitmap(
        dpid=19,
        dpcode="fault",
        dpmode=DPMode.READ,
        label_range=["E1", "E2", "tankfull"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
