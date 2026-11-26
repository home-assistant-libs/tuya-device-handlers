"""Quirk for Gosund SP111 smart plug (37mnhia3pojleqfh).

The cloud declares `cur_voltage` and `cur_power` with `scale=0`, but the
device reports deci-volts and deci-watts (2255 means 225.5 V, 40 means
4.0 W). `cur_current` is already correct in mA and is left untouched.

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
        manufacturer="Gosund",
        model="Smart Plug",
        model_id="SP111",
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
