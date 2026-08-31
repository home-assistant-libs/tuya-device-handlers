"""Extended type information classes for the Tuya integration.

These build on the core classes in :mod:`type_information` to cover common
quirk needs that recur across several devices, so individual quirk files can
import a shared implementation instead of redefining one locally.
"""

from dataclasses import dataclass
from typing import Any

from tuya_sharing import CustomerDevice

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
