"""Tuya device wrapper."""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class TuyaNumberDefinition:
    number_wrapper: DeviceWrapper[float]
