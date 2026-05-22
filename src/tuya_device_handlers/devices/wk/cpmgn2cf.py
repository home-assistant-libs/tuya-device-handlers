"""Quirk for Thermostatic Radiator Valve (product_id cpmgn2cf).

Tuya does not advertise the ``valve`` datapoint (dpid 109) for this device,
so Home Assistant cannot expose the valve opening percentage. It has been
retrieved from the Tuya Developer Portal.

See https://github.com/home-assistant-libs/tuya-device-handlers/issues/207
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="cpmgn2cf")
    .add_dpid_integer(
        dpid=109,
        dpcode="valve",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
