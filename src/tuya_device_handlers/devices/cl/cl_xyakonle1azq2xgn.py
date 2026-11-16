"""Quirk for Tuya blind motor (product_id xyakonle1azq2xgn).

This device always reports percent_state as 0.

To be able to control the device, we need to ignore the
``percent_control`` and ``percent_state`` DPs.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(product_id="xyakonle1azq2xgn")
    .remove_dpid(dpid=9, dpcode="percent_control")
    .remove_dpid(dpid=8, dpcode="percent_state")
    .register(TUYA_QUIRKS_REGISTRY)
)
