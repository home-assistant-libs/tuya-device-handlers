"""Tuya button definition."""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper


@dataclass
class TuyaButtonDefinition:
    button_wrapper: DeviceWrapper[bool]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaButtonDefinition | None:
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaButtonDefinition(button_wrapper=wrapper)
    return None
