"""Definitions for number entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class NumberDefinition:
    number_wrapper: DeviceWrapper[float]
