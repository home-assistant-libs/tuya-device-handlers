"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ..type_information import BitmapTypeInformation
from .common import DPCodeBitmapWrapper, DPCodeWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class DPCodeBitmapBitWrapper(DPCodeBitmapWrapper[bool]):
    """Simple wrapper for a specific bit in bitmap values."""

    def __init__(
        self, dpcode: str, type_information: BitmapTypeInformation, mask: int
    ) -> None:
        """Init DPCodeBitmapWrapper."""
        super().__init__(dpcode, type_information)
        self._mask = mask

    def read_device_status(self, device: CustomerDevice) -> bool | None:
        """Read the device value for the dpcode."""
        if (raw_value := self._read_dpcode_value(device)) is None:
            return None
        return (raw_value & (1 << self._mask)) != 0

    @classmethod
    def find_dpcode(  # type: ignore[override]
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        bitmap_key: str,
    ) -> Self | None:
        """Find and return a DPCodeBitmapBitWrapper for the given DP codes."""
        if (
            type_information := BitmapTypeInformation.find_dpcode(
                device, dpcodes
            )
        ) and bitmap_key in type_information.label:
            return cls(
                type_information.dpcode,
                type_information,
                type_information.label.index(bitmap_key),
            )
        return None


class DPCodeInSetWrapper(DPCodeWrapper[bool]):
    """DPCode Wrapper to check if value is in a set."""

    _valid_values: set[bool | float | int | str]

    def __init__(
        self, dpcode: str, valid_values: set[bool | float | int | str]
    ) -> None:
        """Init DPCodeInSetWrapper."""
        super().__init__(dpcode)
        self._valid_values = valid_values

    def read_device_status(self, device: CustomerDevice) -> bool | None:
        """Read the device value for the dpcode."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        return raw_value in self._valid_values
