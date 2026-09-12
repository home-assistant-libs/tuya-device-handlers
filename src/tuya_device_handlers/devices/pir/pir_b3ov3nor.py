"""Quirk for the b3ov3nor PIR device."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="b3ov3nor")
    # 修正 101 號動態感應 DP：還原為硬體原始的 Boolean 接收
    .add_dpid_boolean(
        dpid=101,
        dpcode="pir",
        dpmode=DPMode.READ,
    )
    # 修正 103 號電量百分比 DP
    .add_dpid_integer(
        dpid=103,
        dpcode="battery_percentage",
        dpmode=DPMode.READ,
        min=0,
        max=100,
        scale=0,
        step=1,
        unit="%",
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
