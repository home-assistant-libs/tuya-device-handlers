"""Definitions for binary sensor entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class BinarySensorDefinition:
    key: str

    binary_sensor_wrapper: DeviceWrapper[bool]
