"""Quirk for Tem&Hum Sensor with Probe."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="m7kacaxrxbxeegfs")
    .add_dpid_integer(
        dpid=101,
        dpcode="ext_temp",
        dpmode=DPMode.READ,
        unit="℃",
        min=-200,
        max=1000,
        scale=1,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
