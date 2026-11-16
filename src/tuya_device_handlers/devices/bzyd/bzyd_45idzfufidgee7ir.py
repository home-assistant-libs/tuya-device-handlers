"""Quirk for the Momcozy Smart White Noise Machine (product 45idzfufidgee7ir).

The device reports colour_data with saturation and value on a 0-1000
scale, while its Json datapoint declares no ranges, so the default
light definition falls back to a 0-255 scale. Every colour preset comes
out washed out and dim. The quirk overrides the colour_data type
information to declare the device's 0-1000 ranges.

See https://github.com/home-assistant/core/issues/188634.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information_ex import (
    ColorDataJsonTypeInformationEx,
)

(
    DeviceQuirk()
    .applies_to(
        product_id="45idzfufidgee7ir",
        manufacturer="Momcozy",
        model="MBZ285",
    )
    .override_dpid_type_information_cls(
        dpid=5,
        dpcode="colour_data",
        type_information_cls=ColorDataJsonTypeInformationEx,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
