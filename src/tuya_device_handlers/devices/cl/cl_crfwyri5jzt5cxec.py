"""Quirk for ZM25RW01 roller blind motor (product_id crfwyri5jzt5cxec).

This device reports and accepts position in the standard HA convention
(0 = closed, 100 = open), but the default CL mapping inverts it, so a closed
blind shows as open and the open button closes it.

Applying ``InvertedIntegerTypeInformationEx`` pre-inverts the value at the
TypeInformation level, so the wrapper's own inversion cancels out.

The quirk is not conditional on ``control_back_mode``: it assumes the motor
is in ``back`` mode, which is how the Tuya app shows it.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(product_id="crfwyri5jzt5cxec")
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
