"""Quirk for Della mini-split (product_id hw50w7qvxluhslkk).

This quirk removes the incorrect temp_set datapoint, allowing the
correct temp_set_f datapoint to be used for temperature control.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(product_id="hw50w7qvxluhslkk")
    .remove_dpid(dpid=2, dpcode="temp_set")
    .register(TUYA_QUIRKS_REGISTRY)
)
