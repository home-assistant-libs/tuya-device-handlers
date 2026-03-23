"""Definitions for light entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class LightDefinition:
    key: str

    brightness_wrapper: DeviceWrapper[int] | None
    color_data_wrapper: DeviceWrapper[tuple[float, float, float]] | None
    color_mode_wrapper: DeviceWrapper[str] | None
    color_temp_wrapper: DeviceWrapper[int] | None
    switch_wrapper: DeviceWrapper[bool]
