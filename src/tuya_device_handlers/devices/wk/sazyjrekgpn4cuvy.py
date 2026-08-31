"""Quirk for Thermostat (product_id sazyjrekgpn4cuvy).

DP 35 (``battery_percentage``) reports on a 0-5 scale instead of the
standard 0-100 percentage, causing a fully charged device to be reported
as 5 %. See https://github.com/home-assistant/core/issues/171131.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information import IntegerTypeInformation


class _BatteryPercentage0To5TypeInformation(IntegerTypeInformation):
    """Battery percentage reported on a 0-5 raw scale.

    The device reports ``battery_percentage`` between 0 and 5, where 5
    means a fully charged battery. Expose the value as the standard
    0-100 % range expected by Home Assistant.
    """

    def scale_value(self, value: int) -> float:
        """Scale a 0-5 raw value to the 0-100 percent range."""
        return value * 20


(
    DeviceQuirk()
    .applies_to(product_id="sazyjrekgpn4cuvy")
    .override_dpid_type_information_cls(
        dpid=35,
        dpcode="battery_percentage",
        type_information_cls=_BatteryPercentage0To5TypeInformation,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
