"""Tuya device wrapper."""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class TuyaCameraDefinition:
    motion_detection_switch: DeviceWrapper[bool] | None
    recording_status: DeviceWrapper[bool] | None
