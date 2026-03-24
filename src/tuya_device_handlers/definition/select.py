"""Tuya select definition."""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeEnumWrapper


@dataclass
class TuyaSelectDefinition:
    select_wrapper: DeviceWrapper[str]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaSelectDefinition | None:
    if wrapper := DPCodeEnumWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaSelectDefinition(select_wrapper=wrapper)
    return None
