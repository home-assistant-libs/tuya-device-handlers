"""Definitions for select entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class TuyaSelectDefinition:
    select_wrapper: DeviceWrapper[str]
