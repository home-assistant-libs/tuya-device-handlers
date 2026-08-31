"""Quirk for the Kogan portable AC crh9iaqFowdJX5UY."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="crh9iaqFowdJX5UY")
    .add_dpid_integer(
        dpid=2,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℃",
        min=16,
        max=30,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=3,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="℃",
        min=-7,
        max=98,
        scale=0,
        step=1,
    )
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["cold", "hot", "wet", "wind"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
