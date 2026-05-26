"""Quirk for cover device zah67ekd (product_id zah67ekd, category cl).

This device reports position in the standard HA convention (0=closed,
100=open). The default CL mapping uses DPCodeInvertedPercentageWrapper
because most Tuya curtain/blind motors report position inverted
(0=open, 100=closed), but that incorrectly flips the position for this
device.

See https://github.com/home-assistant/core/issues/159800.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(product_id="zah67ekd")
    .invert_cover_position(inverted=False)
    .register(TUYA_QUIRKS_REGISTRY)
)
