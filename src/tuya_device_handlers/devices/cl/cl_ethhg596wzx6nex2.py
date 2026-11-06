"""Quirk for Tuya Smart Curtain Motor (product_id ethhg596wzx6nex2).

This device reports and accepts position in the standard HA convention
(0 = closed, 100 = open). The default CL mapping inverts the position,
which causes the displayed position and commands to be reversed.

Applying ``InvertedIntegerTypeInformationEx`` pre-inverts both position
datapoints so the default wrapper's inversion cancels out.

See https://github.com/home-assistant/core/pull/189810.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(product_id="ethhg596wzx6nex2")
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
