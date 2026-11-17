"""Quirk for ZM25RW01 roller blind motor (product_id crfwyri5jzt5cxec).

This device follows ``control_back_mode``: in ``back`` mode it reports and
accepts position in the standard HA convention (0 = closed, 100 = open), and
in ``forward`` mode the position is reversed. The default CL mapping always
inverts it, so in ``back`` mode a closed blind shows as open and the open
button closes it.

Applying ``BackModeInvertedIntegerTypeInformationEx`` pre-inverts the value in
``back`` mode, so the wrapper's own inversion cancels out there.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    BackModeInvertedIntegerTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(product_id="crfwyri5jzt5cxec")
    .override_dpid_type_information_cls(
        dpid=2,
        dpcode="percent_control",
        type_information_cls=BackModeInvertedIntegerTypeInformationEx,
    )
    .override_dpid_type_information_cls(
        dpid=3,
        dpcode="percent_state",
        type_information_cls=BackModeInvertedIntegerTypeInformationEx,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
