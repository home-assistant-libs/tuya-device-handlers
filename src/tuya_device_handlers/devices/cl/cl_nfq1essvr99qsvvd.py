"""Quirk for Tuya blind motor (product_id nfq1essvr99qsvvd).

This device (Canisteo Smart Zebra Shades/Blinds) reports and accepts
position in the standard HA convention (0 = closed, 100 = open).  The
default CL (curtain) mapping wraps both the read DP (``percent_state``)
and the write DP (``percent_control``) in
``DPCodeInvertedPercentageWrapper``, because most Tuya curtain/blind
motors use the opposite convention (0 = open, 100 = closed).

For this device that wrapper is wrong in *both* directions:

* Reads: the reported position is displayed backwards.
* Writes: ``async_open_cover`` sends ``control: "open"`` *and* a
  position command of 100, which the wrapper flips to 0 - so the
  up button drives the blind closed, and vice versa.

Applying ``InvertedIntegerTypeInformationEx`` pre-inverts the value at the
TypeInformation level on both DPs, so the wrapper's own inversion cancels
out and the position is reported and set correctly.

Note that the open/closed *state* was already correct without this quirk:
it is derived from the ``situation_set`` enum DP, which the percentage
wrapper never touches.

See https://github.com/home-assistant/core/issues/159800.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(product_id="nfq1essvr99qsvvd", manufacturer="Canisteo")
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
