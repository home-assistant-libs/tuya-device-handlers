"""Definitions for camera entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper


@dataclass
class CameraDefinition:
    motion_detection_switch: DeviceWrapper[bool] | None
    recording_status: DeviceWrapper[bool] | None
