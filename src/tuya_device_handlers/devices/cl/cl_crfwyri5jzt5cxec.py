"""Quirk for Tuya roller blind motor (product_id crfwyri5jzt5cxec).

This device (ZM25RW01) reports and accepts position in the standard HA
convention (0 = closed, 100 = open) while its ``control_back_mode`` is
``back``. The default CL (curtain) mapping wraps both the read DP
(``percent_state``) and the write DP (``percent_control``) in
``DPCodeInvertedPercentageWrapper``, because most Tuya curtain/blind motors
use the opposite convention (0 = open, 100 = closed).

For this device that wrapper is wrong in *both* directions:

* Reads: a closed blind (``percent_state`` 0) is shown as open at 100%.
* Writes: ``async_open_cover`` sends a position of 100, which the wrapper
  flips to 0 - so the open button drives the blind closed, and vice versa.

Applying ``InvertedIntegerTypeInformationEx`` pre-inverts the value at the
TypeInformation level on both DPs, so the wrapper's own inversion cancels
out and the position is reported and set correctly.

Note that the quirk is not conditional on ``control_back_mode``: it assumes
the motor is in ``back`` mode, which is how the Tuya app shows it.
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
