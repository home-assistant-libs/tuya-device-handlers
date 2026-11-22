"""Fix for MOES 4 Gang ZigBee Scene Remote (abci1hiu)."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="abci1hiu")
    .add_dpid_enum(
        dpid=1,
        dpcode="switch_mode1",
        dpmode=DPMode.READ,
        enum_range=["click", "double_click", "press"],
    )
    .set_dpid_strategy_to_enum(
        dpid=1,
        dpcode="switch_mode1",
        enum_mapping_map={
            "single_click": "click",
            "double_click": "double_click",
            "long_press": "press",
        },
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
