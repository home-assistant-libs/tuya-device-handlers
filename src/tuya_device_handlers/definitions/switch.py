"""Definitions for switch entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class SwitchDefinition:
    switch_wrapper: DeviceWrapper[bool]
