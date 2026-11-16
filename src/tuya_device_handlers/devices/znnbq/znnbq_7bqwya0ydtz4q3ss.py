"""Quirk for WVC micro inverter.

Tuya reports `power_total` as `unit="kW"` with `scale=3`.
For this device the raw value represents watts with scale 3.

Example from diagnostics before applying the quirk:
    raw power_total = 308022

Incorrect interpretation:
    308022 / 1000 = 308.022 kW = 308022 W

Correct interpretation:
    308022 / 1000 = 308.022 W
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="7bqwya0ydtz4q3ss",
        manufacturer="WVC",
        model="Micro inverter",
        model_id="WVC-800W",
    )
    .add_dpid_integer(
        dpid=10,
        dpcode="power_total",
        dpmode=DPMode.READ,
        unit="W",
        min=0,
        max=50000000,
        scale=3,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
