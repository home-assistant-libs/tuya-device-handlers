"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..helpers.homeassistant import TuyaFanDirection
from ..type_information import EnumTypeInformation, IntegerTypeInformation
from .common import DPCodeEnumWrapper
from .extended import DPCodeRemappedIntegerWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class FanDirectionEnumWrapper(DPCodeEnumWrapper[TuyaFanDirection]):
    """Wrapper for fan direction DP code."""

    _MAPPINGS = {
        "forward": TuyaFanDirection.FORWARD,
        "reverse": TuyaFanDirection.REVERSE,
    }

    def __init__(
        self, dpcode: str, type_information: EnumTypeInformation
    ) -> None:
        """Init FanDirectionEnumWrapper."""
        super().__init__(dpcode, type_information)

    def read_device_status(
        self, device: CustomerDevice
    ) -> TuyaFanDirection | None:
        """Read the device status and return the direction string."""
        if (raw_value := self._read_dpcode_value(device)) and (
            value := self._MAPPINGS.get(raw_value)
        ):
            return value
        return None


class FanSpeedIntegerWrapper(DPCodeRemappedIntegerWrapper):
    """Wrapper for fan speed DP code (from an integer).

    Contrary to the standard DPCodePercentageWrapper we start the range at 1.
    """

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init FanSpeedIntegerWrapper."""
        super().__init__(dpcode, type_information, target_min=1, target_max=100)


class FanSpeedEnumWrapper(DPCodeEnumWrapper[int]):
    """Wrapper for fan speed DP code (from an enum)."""

    def read_device_status(self, device: CustomerDevice) -> int | None:
        """Get the current speed as a percentage."""
        if (value := self._read_dpcode_value(device)) is None:
            return None

        list_len = len(self.options)
        list_position = self.options.index(value) + 1
        return (list_position * 100) // list_len

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> Any:
        """Convert a Home Assistant value back to a raw device value."""
        list_len = len(self.options)

        for offset, speed in enumerate(self.options):
            list_position = offset + 1
            upper_bound = (list_position * 100) // list_len
            if value <= upper_bound:
                return speed

        return self.options[-1]
