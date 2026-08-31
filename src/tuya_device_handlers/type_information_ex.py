"""Extended type information classes for the Tuya integration.

These build on the core classes in :mod:`type_information` to cover common
quirk needs that recur across several devices, so individual quirk files can
import a shared implementation instead of redefining one locally.
"""

from dataclasses import dataclass
from typing import Any, ClassVar

from tuya_sharing import CustomerDevice

from .const import ColorTempScale
from .type_information import IntegerTypeInformation


@dataclass(kw_only=True)
class InvertedIntegerTypeInformationEx(IntegerTypeInformation):
    """IntegerTypeInformation that inverts the value within its range.

    Read: returns ``scale_value(max) - value`` instead of ``value``.
    Write: sends ``scale_value(max) - value`` to the device.

    Intended for devices that report a value in the opposite direction to
    what the default wrapper expects.  For example, if the wrapper inverts
    a 0-100 percentage and the device already reports in HA convention
    (0 = closed, 100 = open), applying this class via
    ``override_dpid_type_information_cls`` pre-inverts at the TypeInformation
    level so the wrapper's own inversion cancels out, yielding the correct
    value.

    See https://github.com/home-assistant/core/issues/159800.
    """

    def read_device_value(self, device: CustomerDevice) -> float | None:
        """Read and invert the device value."""
        value = super().read_device_value(device)
        if value is None:
            return None
        return self.scale_value(self.max) - value

    def prepare_set_value(self, device: CustomerDevice, value: Any) -> int:
        """Invert and prepare a value to be sent to the device."""
        if not isinstance(value, (int, float)):
            return super().prepare_set_value(device, value)
        return super().prepare_set_value(
            device, self.scale_value(self.max) - value
        )


@dataclass(kw_only=True)
class ColorTempTypeInformationEx(IntegerTypeInformation):
    """IntegerTypeInformation carrying the physical CCT characteristics.

    The Tuya cloud only reports the raw range of a color temperature
    datapoint (typically 0-1000), never the Kelvin range the lamp
    actually covers, nor whether that raw range is linear in mireds or
    in Kelvin.  `ColorTempWrapper` assumes the Tuya defaults (2000-6500 K,
    linear in mireds); a device that deviates gets a subclass of this
    class applied via ``override_dpid_type_information_cls``, so the
    correction is attached to the individual datapoint rather than to
    the device (a device may expose several lights).

    See https://github.com/home-assistant/core/issues/166103.
    """

    min_kelvin: ClassVar[int] = 2000
    """Warmest color temperature the lamp can produce."""

    max_kelvin: ClassVar[int] = 6500
    """Coldest color temperature the lamp can produce."""

    color_temp_scale: ClassVar[ColorTempScale] = ColorTempScale.MIRED
    """How the raw range maps onto the Kelvin range."""
