"""Definitions for siren entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class SirenDefinition:
    key: str

    siren_wrapper: DeviceWrapper[bool]
