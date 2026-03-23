"""Definitions for switch entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class SwitchDefinition:
    key: str

    switch_wrapper: DeviceWrapper[bool]
