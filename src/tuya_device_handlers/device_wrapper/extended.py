"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..type_information import IntegerTypeInformation
from ..utils import RemapHelper
from .common import DPCodeIntegerWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class DPCodeRoundedIntegerWrapper(DPCodeIntegerWrapper[int]):
    """Wrapper to ensure float values are always rounded."""

    def read_device_status(self, device: CustomerDevice) -> int | None:
        """Read and round the device status."""
        if (value := super()._read_dpcode_value(device)) is None:
            return None
        return round(value)


class DPCodeRemappedIntegerWrapper(DPCodeIntegerWrapper[int]):
    """Wrapper to map Tuya integer values to a custom range."""

    _remap_helper: RemapHelper

    def __init__(
        self,
        dpcode: str,
        type_information: IntegerTypeInformation,
        *,
        target_min: int,
        target_max: int,
    ) -> None:
        """Init DPCodeRemappedIntegerWrapper."""
        super().__init__(dpcode, type_information)
        self._remap_helper = RemapHelper.from_type_information(
            type_information, target_min, target_max
        )

    def _remap_inverted(self, device: CustomerDevice) -> bool:
        """Check if the remap helper should be inverted."""
        return False

    def read_device_status(self, device: CustomerDevice) -> int | None:
        """Read and round the device status."""
        if (value := device.status.get(self.dpcode)) is None:
            return None

        return round(
            self._remap_helper.remap_value_to(
                value, reverse=self._remap_inverted(device)
            )
        )

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> int:
        return round(
            self._remap_helper.remap_value_from(
                value, reverse=self._remap_inverted(device)
            )
        )


class DPCodePercentageWrapper(DPCodeRemappedIntegerWrapper):
    """Wrapper to map Tuya integer values to percentage (0..100)."""

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init DPCodePercentageWrapper."""
        super().__init__(dpcode, type_information, target_min=0, target_max=100)


class DPCodeInvertedPercentageWrapper(DPCodePercentageWrapper):
    """Wrapper to map Tuya integer values to percentage (inverted 100..0)."""

    def _remap_inverted(self, device: CustomerDevice) -> bool:
        """Check if the remap helper should be inverted."""
        return True


class DPCodeNonZeroPercentageWrapper(DPCodeRemappedIntegerWrapper):
    """Wrapper to map Tuya integer values to non-zero percentage (1..100)."""

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init DPCodeNonZeroPercentageWrapper."""
        super().__init__(dpcode, type_information, target_min=1, target_max=100)
