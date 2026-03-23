"""Tuya device wrapper."""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class TuyaSirenDefinition:
    siren_wrapper: DeviceWrapper[bool]
