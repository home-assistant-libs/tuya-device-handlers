"""Definitions for sensor entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class SensorDefinition:
    sensor_wrapper: DeviceWrapper[str | int | float]
