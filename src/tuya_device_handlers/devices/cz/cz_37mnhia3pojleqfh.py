"""Quirk for Smart Plug SP111 (37mnhia3pojleqfh).

The cloud reports wrong type information for the electricity datapoints:

- `cur_voltage` is declared with `scale=0` and unit `V`, but the device
  reports deci-volts (e.g. 2255 means 225.5 V), so Home Assistant shows
  "2255 V" instead of 225.5 V.
- `cur_power` is declared with `scale=0` and unit `W`, but the device
  reports deci-watts (e.g. 40 means 4.0 W).

The `scale=1` assumption is confirmed by the device's own report, which is
internally consistent only when both values are divided by ten: it carries
`cur_voltage=2255`, `cur_current=18` and `cur_power=40`, and
225.5 V x 18 mA = 4.06 W matches `cur_power` of 4.0 W, whereas
2255 V x 18 mA = 40.6 W contradicts it by a factor of ten.

`cur_current` is declared in `mA` with `scale=0` and is already correct
(18 means 18 mA), so it is intentionally left untouched.

The voltage maximum is raised from 2500 to 5000 so that mains voltages
above 250.0 V are not discarded as out-of-range after rescaling.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="37mnhia3pojleqfh",
        manufacturer="Tuya",
        model="SP111",
        model_id="37mnhia3pojleqfh",
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
    .register(TUYA_QUIRKS_REGISTRY)
)
