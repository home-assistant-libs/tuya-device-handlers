"""Quirk for Tuya curtain motor (product_id cf1sl3tj).

This device reports ``percent_state`` in the standard HA convention
(0 = closed, 100 = open).  The default CL mapping uses
``DPCodeInvertedPercentageWrapper`` because most Tuya curtain/blind motors
report position inverted (0 = open, 100 = closed), which causes the
position to be displayed and set backwards for this device.

Applying ``InvertedIntegerTypeInformationEx`` pre-inverts the value at the
TypeInformation level, so the wrapper's own inversion cancels out and the
position is reported and set correctly.

See https://github.com/home-assistant/core/issues/159800.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(product_id="cf1sl3tj")
    .override_dpid_type_information_cls(
        dpid=2,
        dpcode="percent_control",
        type_information_cls=InvertedIntegerTypeInformationEx,
    )
    .override_dpid_type_information_cls(
        dpid=3,
        dpcode="percent_state",
        type_information_cls=InvertedIntegerTypeInformationEx,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
