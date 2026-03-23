"""Definitions for valve entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class ValveDefinition:
    key: str

    control_wrapper: DeviceWrapper[bool]
