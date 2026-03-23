"""Definitions for vacuum entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper
from ..helpers.homeassistant import TuyaVacuumAction, TuyaVacuumActivity


@dataclass
class VacuumDefinition:
    action_wrapper: DeviceWrapper[TuyaVacuumAction] | None
    activity_wrapper: DeviceWrapper[TuyaVacuumActivity] | None
    fan_speed_wrapper: DeviceWrapper[str] | None
