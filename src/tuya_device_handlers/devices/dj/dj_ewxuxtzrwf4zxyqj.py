"""Quirk for Smart bulb (product_id ewxuxtzrwf4zxyqj).

The device reports color temperature as a 0-1000 relative scale, but
the physical CCT range is 1600-4000 K rather than the Tuya default
of 2000-6500 K. Home Assistant therefore shows the wrong Kelvin
slider and automation range.

See https://github.com/home-assistant/core/issues/166103.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(product_id="ewxuxtzrwf4zxyqj")
    .set_color_temp_kelvin_range(min_kelvin=1600, max_kelvin=4000)
    .register(TUYA_QUIRKS_REGISTRY)
)
