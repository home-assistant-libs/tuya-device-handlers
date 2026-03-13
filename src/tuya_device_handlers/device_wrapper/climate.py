"""Tuya device wrapper."""

from __future__ import annotations

import collections
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from ..helpers.homeassistant import TuyaClimateHVACMode, TuyaClimateSwingMode
from ..type_information import EnumTypeInformation
from .base import DeviceWrapper
from .common import DPCodeBooleanWrapper, DPCodeEnumWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

_DEFAULT_DEVICE_MODE_TO_HVACMODE = {
    "auto": TuyaClimateHVACMode.HEAT_COOL,
    "cold": TuyaClimateHVACMode.COOL,
    "freeze": TuyaClimateHVACMode.COOL,
    "heat": TuyaClimateHVACMode.HEAT,
    "hot": TuyaClimateHVACMode.HEAT,
    "manual": TuyaClimateHVACMode.HEAT_COOL,
    "off": TuyaClimateHVACMode.OFF,
    "wet": TuyaClimateHVACMode.DRY,
    "wind": TuyaClimateHVACMode.FAN_ONLY,
}


@dataclass(kw_only=True)
class SwingModeCompositeWrapper(DeviceWrapper[str]):
    """Wrapper for managing swing mode across multiple boolean DPCodes.

    on/off lookup based for "swing" or "shake"
    horizontal lookup based on "switch_horizontal"
    vertical lookup based on "switch_vertical"
    """

    on_off: DPCodeBooleanWrapper | None = None
    horizontal: DPCodeBooleanWrapper | None = None
    vertical: DPCodeBooleanWrapper | None = None
    options: list[str]

    @classmethod
    def find_dpcode(cls, device: CustomerDevice) -> Self | None:
        """Find and return a _SwingModeWrapper for the given DP codes."""
        on_off = DPCodeBooleanWrapper.find_dpcode(
            device, ("swing", "shake"), prefer_function=True
        )
        horizontal = DPCodeBooleanWrapper.find_dpcode(
            device, "switch_horizontal", prefer_function=True
        )
        vertical = DPCodeBooleanWrapper.find_dpcode(
            device, "switch_vertical", prefer_function=True
        )
        if on_off or horizontal or vertical:
            options: list[str] = [TuyaClimateSwingMode.OFF]
            if on_off:
                options.append(TuyaClimateSwingMode.ON)
            if horizontal:
                options.append(TuyaClimateSwingMode.HORIZONTAL)
            if vertical:
                options.append(TuyaClimateSwingMode.VERTICAL)
            return cls(
                on_off=on_off,
                horizontal=horizontal,
                vertical=vertical,
                options=options,
            )
        return None

    def read_device_status(self, device: CustomerDevice) -> str | None:
        """Read the device swing mode."""
        if self.on_off and self.on_off.read_device_status(device):
            return TuyaClimateSwingMode.ON

        horizontal = (
            self.horizontal.read_device_status(device)
            if self.horizontal
            else None
        )
        vertical = (
            self.vertical.read_device_status(device) if self.vertical else None
        )
        if horizontal and vertical:
            return TuyaClimateSwingMode.BOTH
        if horizontal:
            return TuyaClimateSwingMode.HORIZONTAL
        if vertical:
            return TuyaClimateSwingMode.VERTICAL

        return TuyaClimateSwingMode.OFF

    def get_update_commands(
        self, device: CustomerDevice, value: str
    ) -> list[dict[str, Any]]:
        """Set new target swing operation."""
        commands = []
        if self.on_off:
            commands.extend(
                self.on_off.get_update_commands(
                    device, value == TuyaClimateSwingMode.ON
                )
            )

        if self.vertical:
            commands.extend(
                self.vertical.get_update_commands(
                    device,
                    value
                    in (
                        TuyaClimateSwingMode.BOTH,
                        TuyaClimateSwingMode.VERTICAL,
                    ),
                )
            )
        if self.horizontal:
            commands.extend(
                self.horizontal.get_update_commands(
                    device,
                    value
                    in (
                        TuyaClimateSwingMode.BOTH,
                        TuyaClimateSwingMode.HORIZONTAL,
                    ),
                )
            )
        return commands


def _filter_hvac_mode_mappings(
    tuya_range: list[str],
) -> dict[str, TuyaClimateHVACMode | None]:
    """Filter TUYA_HVAC_TO_HA modes that are not in the range.

    If multiple Tuya modes map to the same HA mode, set the mapping to None to avoid
    ambiguity when converting back from HA to Tuya modes.
    """
    modes_in_range = {
        tuya_mode: _DEFAULT_DEVICE_MODE_TO_HVACMODE.get(tuya_mode)
        for tuya_mode in tuya_range
    }
    modes_occurrences = collections.Counter(modes_in_range.values())
    for key, value in modes_in_range.items():
        if value is not None and modes_occurrences[value] > 1:
            modes_in_range[key] = None
    return modes_in_range


class DefaultHVACModeWrapper(DPCodeEnumWrapper[TuyaClimateHVACMode]):
    """Wrapper for managing climate HVACMode."""

    # Modes that do not map to HVAC modes are ignored (they are handled by PresetWrapper)

    def __init__(
        self, dpcode: str, type_information: EnumTypeInformation
    ) -> None:
        """Init DefaultHVACModeWrapper."""
        super().__init__(dpcode, type_information)
        self._mappings = _filter_hvac_mode_mappings(type_information.range)
        self.options = [
            ha_mode
            for ha_mode in self._mappings.values()
            if ha_mode is not None
        ]

    def read_device_status(
        self, device: CustomerDevice
    ) -> TuyaClimateHVACMode | None:
        """Read the device status."""
        if (raw := self._read_dpcode_value(device)) not in self._mappings:
            return None
        return self._mappings[raw]

    def _convert_value_to_raw_value(
        self,
        device: CustomerDevice,
        value: TuyaClimateHVACMode,
    ) -> Any:
        """Convert value to raw value."""
        return next(
            tuya_mode
            for tuya_mode, ha_mode in self._mappings.items()
            if ha_mode == value
        )


class DefaultPresetModeWrapper(DPCodeEnumWrapper):
    """Wrapper for managing climate preset modes."""

    # Modes that map to HVAC modes are ignored (they are handled by HVACModeWrapper)

    def __init__(
        self, dpcode: str, type_information: EnumTypeInformation
    ) -> None:
        """Init DefaultPresetModeWrapper."""
        super().__init__(dpcode, type_information)
        mappings = _filter_hvac_mode_mappings(type_information.range)
        self.options = [
            tuya_mode
            for tuya_mode, ha_mode in mappings.items()
            if ha_mode is None
        ]

    def read_device_status(self, device: CustomerDevice) -> str | None:
        """Read the device status."""
        if (raw := self._read_dpcode_value(device)) in self.options:
            return raw
        return None
