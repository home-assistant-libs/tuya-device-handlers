"""Quirk for BHT-002 style thermostat (product_id IAYz2WK1th0cMLmL).

The device counts temperatures in half degrees (e.g. 45 = 22.5 °C), but
the cloud declares them as tenths (``temp_set``, scale 1) and whole
degrees (``upper_temp``, scale 0). Home Assistant therefore shows a target
temperature of 4.6 °C instead of 23 °C, a target range of 1-7 °C instead
of 5-35 °C, and a current temperature of 45 °C instead of 22.5 °C.

DP 3 is declared as ``upper_temp`` but holds the measured room temperature.
It is kept under that DPCode, which the default climate definition already
reads as the current temperature.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode
from tuya_device_handlers.type_information import IntegerTypeInformation


class HalfDegreeIntegerTypeInformation(IntegerTypeInformation):
    """Integer datapoint counted in half degrees."""

    def scale_value(self, value: int) -> float:
        """Scale a value."""
        return value / 2

    def scale_value_back(self, value: float) -> int:
        """Return raw value for scaled."""
        return round(value * 2)


(
    DeviceQuirk()
    .applies_to(product_id="IAYz2WK1th0cMLmL")
    # Declared with a step of 5 (2.5 °C once halved), the device accepts
    # 0.5 °C steps
    .add_dpid_integer(
        dpid=2,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℃",
        min=10,
        max=70,
        scale=0,
        step=1,
    )
    .override_dpid_type_information_cls(
        dpid=2,
        dpcode="temp_set",
        type_information_cls=HalfDegreeIntegerTypeInformation,
    )
    .override_dpid_type_information_cls(
        dpid=3,
        dpcode="upper_temp",
        type_information_cls=HalfDegreeIntegerTypeInformation,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
