"""Quirk for Tuya curtain motor (product_id cf1sl3tj).

This device reports ``percent_state`` in the standard HA convention
(0 = closed, 100 = open).  The default CL mapping uses
``DPCodeInvertedPercentageWrapper`` because most Tuya curtain/blind motors
report position inverted (0 = open, 100 = closed), which causes the
position to be displayed and set backwards for this device.

Applying ``_InvertedIntegerTypeInformationEx`` pre-inverts the value at the
TypeInformation level, so the wrapper's own inversion cancels out and the
position is reported and set correctly.

See https://github.com/home-assistant/core/issues/159800.
"""

from dataclasses import dataclass
from typing import Any

from tuya_sharing import CustomerDevice

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.type_information import IntegerTypeInformation


@dataclass(kw_only=True)
class _InvertedIntegerTypeInformationEx(IntegerTypeInformation):
    """IntegerTypeInformation that inverts the value within its range.

    Read: returns ``scale_value(max) - value`` instead of ``value``.
    Write: sends ``max - scale_value_back(value)`` to the device.

    Intended for devices that report a value in the opposite direction to
    what the default wrapper expects.  For example, if the wrapper inverts
    a 0-100 percentage and the device already reports in HA convention
    (0 = closed, 100 = open), applying this class via
    ``override_dpid_type_information_cls`` pre-inverts at the TypeInformation
    level so the wrapper's own inversion cancels out, yielding the correct
    value.
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


(
    DeviceQuirk()
    .applies_to(product_id="cf1sl3tj")
    .override_dpid_type_information_cls(
        dpid=2,
        dpcode="percent_control",
        type_information_cls=_InvertedIntegerTypeInformationEx,
    )
    .override_dpid_type_information_cls(
        dpid=3,
        dpcode="percent_state",
        type_information_cls=_InvertedIntegerTypeInformationEx,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
