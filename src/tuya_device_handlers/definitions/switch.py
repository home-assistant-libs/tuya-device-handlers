"""Definitions for switch entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class TuyaSwitchDefinition:
    switch_wrapper: DeviceWrapper[bool]
