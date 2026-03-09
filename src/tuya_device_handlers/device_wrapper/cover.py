"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..helpers.homeassistant import TuyaCoverAction
from ..type_information import EnumTypeInformation
from .common import DPCodeBooleanWrapper, DPCodeEnumWrapper
from .extended import DPCodePercentageWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class ControlBackModePercentageMappingWrapper(DPCodePercentageWrapper):
    """Wrapper for a cover with control_back_mode support.

    For historical reason, the default is for inversion to be active if
    `control_back_mode` is not set to "back":
    - "back" => not inverted
    - "forward" => inverted
    - None => inverted
    """

    def _remap_inverted(self, device: CustomerDevice) -> bool:
        """Check if the remap helper should be inverted."""
        return bool(device.status.get("control_back_mode") != "back")


class CoverInstructionBooleanWrapper(DPCodeBooleanWrapper[TuyaCoverAction]):
    """Wrapper for boolean-based open/close instructions."""

    options = ["open", "close"]
    _ACTION_MAPPINGS = {
        TuyaCoverAction.OPEN: True,
        TuyaCoverAction.CLOSE: False,
    }

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: TuyaCoverAction
    ) -> bool:
        return self._ACTION_MAPPINGS[value]


class CoverInstructionEnumWrapper(DPCodeEnumWrapper[TuyaCoverAction]):
    """Wrapper for enum-based open/close/stop instructions."""

    _ACTION_MAPPINGS = {
        TuyaCoverAction.OPEN: "open",
        TuyaCoverAction.CLOSE: "close",
        TuyaCoverAction.STOP: "stop",
    }

    def __init__(
        self, dpcode: str, type_information: EnumTypeInformation
    ) -> None:
        super().__init__(dpcode, type_information)
        self.options = [
            ha_action
            for ha_action, tuya_action in self._ACTION_MAPPINGS.items()
            if tuya_action in type_information.range
        ]

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: TuyaCoverAction
    ) -> str:
        return self._ACTION_MAPPINGS[value]


class CoverInstructionSpecialEnumWrapper(CoverInstructionEnumWrapper):
    """Wrapper for enum-based instructions with special values (FZ/ZZ/STOP)."""

    _ACTION_MAPPINGS = {
        TuyaCoverAction.OPEN: "FZ",
        TuyaCoverAction.CLOSE: "ZZ",
        TuyaCoverAction.STOP: "STOP",
    }


class CoverClosedBooleanWrapper(DPCodeBooleanWrapper):
    """Boolean wrapper for checking if cover is closed (inverted)."""

    def read_device_status(self, device: CustomerDevice) -> bool | None:
        if (value := self._read_dpcode_value(device)) is None:
            return None
        return not value


class CoverClosedEnumWrapper(DPCodeEnumWrapper[bool]):
    """Enum wrapper for checking if state is closed."""

    _MAPPINGS = {
        "close": True,
        "fully_close": True,
        "open": False,
        "fully_open": False,
    }

    def read_device_status(self, device: CustomerDevice) -> bool | None:
        if (value := self._read_dpcode_value(device)) is None:
            return None
        return self._MAPPINGS.get(value)
