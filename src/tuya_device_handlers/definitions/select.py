"""Definitions for select entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class SelectDefinition:
    select_wrapper: DeviceWrapper[str]
