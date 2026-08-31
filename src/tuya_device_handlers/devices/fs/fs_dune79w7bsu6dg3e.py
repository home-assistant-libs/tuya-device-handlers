"""Quirk for Duux Whisper Flex fan (product_id dune79w7bsu6dg3e).

Tuya reports the cached status of the horizontal and vertical oscillation
datapoints as lowercase boolean strings despite advertising them as Boolean
values, and maps the local strategy values to the same strings.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(
        product_id="dune79w7bsu6dg3e",
        manufacturer="Duux",
        model="Whisper Flex",
        model_id="DXCF10",
    )
    .map_dpid_initial_status_values(
        dpid=4,
        dpcode="switch_horizontal",
        status_mapping={"false": False, "true": True},
    )
    .set_dpid_strategy_to_enum(
        dpid=4,
        dpcode="switch_horizontal",
        enum_mapping_map={0: False, 1: True},
    )
    .map_dpid_initial_status_values(
        dpid=5,
        dpcode="switch_vertical",
        status_mapping={"false": False, "true": True},
    )
    .set_dpid_strategy_to_enum(
        dpid=5,
        dpcode="switch_vertical",
        enum_mapping_map={0: False, 1: True},
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
