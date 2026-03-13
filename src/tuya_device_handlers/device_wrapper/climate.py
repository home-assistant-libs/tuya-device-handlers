"""Tuya device wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from ..helpers.homeassistant import TuyaClimateSwingMode
from .base import DeviceWrapper
from .common import DPCodeBooleanWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


@dataclass(kw_only=True)
class SwingModeCompositeWrapper(DeviceWrapper[str]):
    """Wrapper for managing climate swing mode operations across multiple DPCodes.

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
