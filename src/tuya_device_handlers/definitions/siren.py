"""Definitions for siren entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class SirenDefinition:
    siren_wrapper: DeviceWrapper[bool]
