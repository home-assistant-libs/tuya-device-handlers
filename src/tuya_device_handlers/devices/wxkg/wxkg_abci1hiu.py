"""Fix for MOES 4 Gang ZigBee Scene Remote (abci1hiu).

Tuya declares button 1 (DPID 1) as switch1_value with single_click,
double_click and long_press. Buttons 2-4 use switch_mode2 through
switch_mode4 with click, double_click and press. Expose button 1 as
switch_mode1 and normalize its values so Home Assistant can create
its event entity.
"""

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
