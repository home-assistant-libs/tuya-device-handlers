"""Quirk for Della mini-split (product_id hw50w7qvxluhslkk).

This quirk forces the temp_set datapoint to advertise a Fahrenheit unit
so Home Assistant treats it as a Fahrenheit temperature control, and
removes the redundant temp_set_f datapoint.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="hw50w7qvxluhslkk")
    .add_dpid_integer(
        dpid=2,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℉",
        min=160,
        max=880,
        scale=1,
        step=5,
    )
    .remove_dpid(dpid=136, dpcode="temp_set_f")
    .register(TUYA_QUIRKS_REGISTRY)
)
