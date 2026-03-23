"""Definitions for event entity"""

from dataclasses import dataclass
from typing import Any

from ..device_wrapper import DeviceWrapper


@dataclass
class EventDefinition:
    key: str

    event_wrapper: DeviceWrapper[tuple[str, dict[str, Any] | None]]
