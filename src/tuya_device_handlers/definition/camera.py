"""Tuya camera definition."""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper


@dataclass
class TuyaCameraDefinition:
    motion_detection_switch: DeviceWrapper[bool] | None
    recording_status: DeviceWrapper[bool] | None


def get_default_definition(device: CustomerDevice) -> TuyaCameraDefinition:
    return TuyaCameraDefinition(
        motion_detection_switch=DPCodeBooleanWrapper.find_dpcode(
            device, "motion_switch", prefer_function=True
        ),
        recording_status=DPCodeBooleanWrapper.find_dpcode(
            device, "record_switch"
        ),
    )
