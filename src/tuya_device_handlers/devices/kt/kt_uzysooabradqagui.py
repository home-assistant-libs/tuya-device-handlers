"""Quirk for Fahrenheit variants of uzysooabradqagui (mini-split heat pump).

The cloud definition advertises temp_set (dpid 2) as Celsius over a 160-880
range at scale 1, but these units report the Fahrenheit setpoint in tenths:
a 68 F setpoint is reported as 680. Home Assistant trusts the advertised unit
and converts, so the setpoint surfaces as 154 F and the range as 61-190 F.

The cloud definition is identical to hw50w7qvxluhslkk, including the redundant
temp_set_f datapoint, so the same detection applies: a Celsius setpoint sits in
the 160-310 range, well below the 610-880 a Fahrenheit unit reports.

For Fahrenheit variants this quirk advertises temp_set in Fahrenheit so Home
Assistant stops converting it, and removes the redundant temp_set_f datapoint,
which the firmware never updates - it stays pinned at its 61 minimum regardless
of the real setpoint.
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
    .applies_to(product_id="uzysooabradqagui")
    .add_dpid_integer(
        dpid=2,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℉",
        min=610,
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
