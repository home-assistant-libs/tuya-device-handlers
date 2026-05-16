"""Quirk for DH-24 Nexi ION UV Wifi dehumidifier."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="uhtamgih7kkdcqtx",
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
        dpid=103,
        dpcode="temp_indoor",
        dpmode=DPMode.READ,
        unit="°C",
        min=-20,
        max=60,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
