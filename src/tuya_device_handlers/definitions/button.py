"""Definitions for button entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class ButtonDefinition:
    key: str

    button_wrapper: DeviceWrapper[bool]
