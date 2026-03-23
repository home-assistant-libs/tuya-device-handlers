"""Definitions for sensor entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class SensorDefinition:
    key: str

    sensor_wrapper: DeviceWrapper[str | int | float]
