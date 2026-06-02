"""Quirk for Smart Socket (wifvoilfrqeo6hvu).

The cloud reports wrong type information for the electricity datapoints:

- `cur_voltage` and `cur_power` are declared with `scale=0`, but the
  device reports deci-volts and deci-watts (e.g. 2306 means 230.6 V).
- `add_ele` is declared with the unit `度` (Chinese for kWh) and
  `scale=0`, but the device reports increments of 0.001 kWh.

The voltage maximum is raised from 2500 to 5000 so that mains voltages
above 250.0 V are not discarded as out-of-range after rescaling.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="wifvoilfrqeo6hvu",
        manufacturer="Gosund",
        model="Smart socket",
        model_id="EP2",
    )
    .add_dpid_integer(
        dpid=3,
        dpcode="add_ele",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=500000,
        scale=3,
        step=1,
        report_type="sum",
    )
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
        max=5000,
        scale=1,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
