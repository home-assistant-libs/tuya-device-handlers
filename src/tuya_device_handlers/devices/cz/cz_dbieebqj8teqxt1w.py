"""Quirk for Smart Plug (dbieebqj8teqxt1w).

The cloud reports incorrect scaling for the electricity datapoints:

- `cur_power` is declared with `scale=0`, but the device reports
  deci-watts (e.g. 3471 means 347.1 W).
- `cur_voltage` is declared with `scale=0`, but the device reports
  deci-volts (e.g. 2417 means 241.7 V).
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="dbieebqj8teqxt1w")
    .add_dpid_integer(
        dpid=5,
        dpcode="cur_power",
        dpmode=DPMode.READ,
        unit="W",
        min=0,
        max=50000,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=6,
        dpcode="cur_voltage",
        dpmode=DPMode.READ,
        unit="V",
        min=0,
        max=2500,
        scale=1,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
