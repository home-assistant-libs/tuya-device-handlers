"""Tuya switch definition."""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper


@dataclass
class TuyaSwitchDefinition:
    switch_wrapper: DeviceWrapper[bool]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaSwitchDefinition | None:
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaSwitchDefinition(switch_wrapper=wrapper)
    return None
