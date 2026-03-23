"""Definitions for fan entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper
from ..helpers.homeassistant import TuyaFanDirection


@dataclass
class FanDefinition:
    direction_wrapper: DeviceWrapper[TuyaFanDirection] | None
    mode_wrapper: DeviceWrapper[str] | None
    oscillate_wrapper: DeviceWrapper[bool] | None
    speed_wrapper: DeviceWrapper[int] | None
    switch_wrapper: DeviceWrapper[bool] | None
