"""Tuya switch definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class SwitchDefinition:
    """Definition for a switch entity."""

    switch_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class SwitchQuirk(BaseEntityQuirk):
    """Definition for a switch entity."""

    definition_fn: Callable[
        [CustomerDevice],
        SwitchDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> SwitchDefinition | None:
    """Get the default switch definition for a device."""
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return SwitchDefinition(switch_wrapper=wrapper)
    return None
