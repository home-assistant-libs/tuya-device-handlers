"""Definitions for humidifier entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class HumidifierDefinition:
    current_humidity_wrapper: DeviceWrapper[int] | None = None
    mode_wrapper: DeviceWrapper[str] | None = None
    switch_wrapper: DeviceWrapper[bool] | None = None
    target_humidity_wrapper: DeviceWrapper[int] | None = None
