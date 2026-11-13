"""Quirk for EVOL Beer & Wine JC-115 cooler (product_id z3srxdwcicg3bla4).

Tuya reports this cooler under the category `jg`, which Home Assistant
doesn't know, so no entities are created. Treat it as an air conditioner to
get a climate entity.

Upstream issue: https://github.com/home-assistant/core/issues/183166
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(product_id="z3srxdwcicg3bla4")
    .override_category("kt")
    .register(TUYA_QUIRKS_REGISTRY)
)
