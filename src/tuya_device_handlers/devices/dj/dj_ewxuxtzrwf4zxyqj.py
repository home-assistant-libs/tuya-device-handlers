"""Quirk for Smart bulb (product_id ewxuxtzrwf4zxyqj).

The device reports color temperature on a 0-1000 raw scale, but the
physical CCT range is 1600-4000 K rather than the Tuya default of
2000-6500 K, and that raw scale is linear in Kelvin rather than in
mireds. Home Assistant therefore shows the wrong Kelvin range and
sets the wrong color temperature.

See https://github.com/home-assistant/core/issues/166103.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import ColorTempScale
from tuya_device_handlers.type_information_ex import ColorTempTypeInformationEx


class BulbColorTempTypeInformation(ColorTempTypeInformationEx):
    """Color temperature characteristics of this bulb."""

    min_kelvin = 1600
    max_kelvin = 4000
    color_temp_scale = ColorTempScale.KELVIN


(
    DeviceQuirk()
    .applies_to(product_id="ewxuxtzrwf4zxyqj")
    .override_dpid_type_information_cls(
        dpid=23,
        dpcode="temp_value_v2",
        type_information_cls=BulbColorTempTypeInformation,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
