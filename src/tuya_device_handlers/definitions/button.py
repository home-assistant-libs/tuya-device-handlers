"""Definitions for button entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class ButtonDefinition:
    button_wrapper: DeviceWrapper[bool]
