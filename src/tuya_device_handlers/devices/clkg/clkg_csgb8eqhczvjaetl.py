"""Quirk for Tuya 6Gen Roller Shutter Switch (product_id csgb8eqhczvjaetl).

This device reports its position in the opposite direction to the default
CLKG mapping in both ``control_back_mode`` values, which causes the position
to be displayed and set backwards.

Applying ``ForwardModeInvertedIntegerTypeInformationEx`` pre-inverts the value
in ``forward`` mode, so the wrapper's own inversion cancels out there and
remains active in ``back`` mode.

See https://github.com/home-assistant/core/issues/159800.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    ForwardModeInvertedIntegerTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(product_id="csgb8eqhczvjaetl")
    .override_dpid_type_information_cls(
        dpid=2,
        dpcode="percent_control",
        type_information_cls=ForwardModeInvertedIntegerTypeInformationEx,
    )
    .override_dpid_type_information_cls(
        dpid=3,
        dpcode="percent_state",
        type_information_cls=ForwardModeInvertedIntegerTypeInformationEx,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
