"""Quirk for Metered electrical outlet (QH3oyDNHKw9c1irH).

The cloud reports wrong type information for the electricity datapoints:

- `cur_power` is declared with `scale=0`, but the device reports
  deci-watts (e.g. 4681 means 468.1 W).
- `cur_voltage` is declared with `scale=0`, but the device reports
  deci-volts (e.g. 1156 means 115.6 V).
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="QH3oyDNHKw9c1irH")
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
