"""Tuya select definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class SelectDefinition:
    """Definition for a select entity."""

    select_wrapper: DeviceWrapper[str]


@dataclass(kw_only=True)
class SelectQuirk(BaseEntityQuirk):
    """Quirk for a select entity."""

    definition_fn: Callable[
        [CustomerDevice],
        SelectDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> SelectDefinition | None:
    """Get the default select definition for a device."""
    if wrapper := DPCodeEnumWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return SelectDefinition(select_wrapper=wrapper)
    return None
