"""Quirk for Duux Whisper Flex fan (product_id dune79w7bsu6dg3e).

Tuya maps the horizontal and vertical oscillation datapoints to lowercase
boolean strings despite advertising them as Boolean values.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    StringBooleanTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(
        product_id="dune79w7bsu6dg3e",
        manufacturer="Duux",
        model="Whisper Flex",
        model_id="DXCF10",
    )
    .override_dpid_type_information_cls(
        dpid=4,
        dpcode="switch_horizontal",
        type_information_cls=StringBooleanTypeInformationEx,
    )
    .set_dpid_strategy_to_enum(
        dpid=4,
        dpcode="switch_horizontal",
        enum_mapping_map={0: False, 1: True},
    )
    .override_dpid_type_information_cls(
        dpid=5,
        dpcode="switch_vertical",
        type_information_cls=StringBooleanTypeInformationEx,
    )
    .set_dpid_strategy_to_enum(
        dpid=5,
        dpcode="switch_vertical",
        enum_mapping_map={0: False, 1: True},
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
