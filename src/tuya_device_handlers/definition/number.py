"""Tuya number definition."""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeIntegerWrapper


@dataclass
class TuyaNumberDefinition:
    number_wrapper: DeviceWrapper[float]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaNumberDefinition | None:
    if wrapper := DPCodeIntegerWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaNumberDefinition(number_wrapper=wrapper)
    return None
