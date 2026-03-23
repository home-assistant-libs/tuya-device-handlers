"""Tuya device wrapper."""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class TuyaSelectDefinition:
    select_wrapper: DeviceWrapper[str]
