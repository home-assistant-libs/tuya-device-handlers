"""Definitions for cover entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper
from ..helpers.homeassistant import TuyaCoverAction


@dataclass
class CoverDefinition:
    key: str

    current_position_wrapper: DeviceWrapper[int] | None
    current_state_wrapper: DeviceWrapper[bool] | None
    instruction_wrapper: DeviceWrapper[TuyaCoverAction] | None
    set_position_wrapper: DeviceWrapper[int] | None
    tilt_position_wrapper: DeviceWrapper[int] | None
