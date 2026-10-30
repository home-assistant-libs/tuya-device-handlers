"""Quirk for Pro Breeze 30L Compressor Dehumidifier (ipmyy4nigpqcnd8q).

The cloud only exposes a phantom `anion` datapoint (DP 5, absent on this
model) plus `fault` and `countdown_left`. This quirk removes `anion`, adds
the real datapoints under the standard `cs` DPCodes and labels bit 3 of the
`fault` bitmap as `tankfull`.

Limitation: the Tuya cloud rejects every command for this product with
error `2008` (command or value not supported), so the added datapoints are
effectively read-only in Home Assistant. They are still declared writable
so the entities match the device's capabilities.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="ipmyy4nigpqcnd8q")
    .remove_dpid(dpid=5, dpcode="anion")
    .add_dpid_boolean(
        dpid=1,
        dpcode="switch",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["0", "1"],  # 0 = auto, 1 = continuous
    )
    .add_dpid_integer(
        dpid=3,
        dpcode="humidity_indoor",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=4,
        dpcode="dehumidify_set_value",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="%",
        min=30,
        max=80,
        scale=0,
        step=5,
    )
    .add_dpid_enum(
        dpid=6,
        dpcode="fan_speed_enum",
        dpmode=DPMode.READ | DPMode.WRITE,
        # 1 = low, 0 = high: the order sets the fan percentage
        enum_range=["1", "0"],
    )
    .add_dpid_boolean(
        dpid=7,
        dpcode="child_lock",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    .add_dpid_bitmap(
        dpid=11,
        dpcode="fault",
        dpmode=DPMode.READ,
        label_range=["e0", "e1", "e2", "tankfull", "e4", "e5"],
    )
    .add_dpid_enum(
        dpid=12,
        dpcode="countdown_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=[str(h) for h in range(25)],  # hours, 0 = off
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
