"""Tuya camera definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class CameraDefinition:
    motion_detection_switch: DeviceWrapper[bool] | None
    recording_status: DeviceWrapper[bool] | None


# Deprecated alias for backward compatibility
TuyaCameraDefinition = CameraDefinition


@dataclass(kw_only=True)
class CameraQuirk(BaseEntityQuirk):
    """Quirk for a camera entity."""

    definition_fn: Callable[
        [CustomerDevice],
        CameraDefinition | None,
    ]


def get_default_definition(device: CustomerDevice) -> CameraDefinition:
    return CameraDefinition(
        motion_detection_switch=DPCodeBooleanWrapper.find_dpcode(
            device, "motion_switch", prefer_function=True
        ),
        recording_status=DPCodeBooleanWrapper.find_dpcode(
            device, "record_switch"
        ),
    )
