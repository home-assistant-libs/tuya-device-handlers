"""Quirk for Fahrenheit variants of hw50w7qvxluhslkk (eg. Della mini-split).

This product_id is shared between regional variants: some units report
temp_set as 10x the Fahrenheit temperature, others as 10x the Celsius
temperature (matching the cloud definition). The cloud definition is
identical for both, but the reported setpoint ranges do not overlap
(160-310 for Celsius, 610-880 for Fahrenheit), so the current status
value is used to detect the Fahrenheit variants.

For Fahrenheit variants, this quirk forces the temp_set datapoint to
advertise a Fahrenheit unit so Home Assistant treats it as a Fahrenheit
temperature control, and removes the redundant temp_set_f datapoint.
Celsius variants are left untouched.
"""

from tuya_sharing import CustomerDevice

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode


def _is_fahrenheit_variant(device: CustomerDevice) -> bool:
    """Check if the device reports temp_set in Fahrenheit."""
    raw_value = device.status.get("temp_set")
    return isinstance(raw_value, int) and raw_value >= 450


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
        apply_when=_is_fahrenheit_variant,
    )
    .remove_dpid(
        dpid=136,
        dpcode="temp_set_f",
        apply_when=_is_fahrenheit_variant,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
