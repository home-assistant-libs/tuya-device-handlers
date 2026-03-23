"""Tuya device wrapper."""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class TuyaButtonDefinition:
    button_wrapper: DeviceWrapper[bool]
