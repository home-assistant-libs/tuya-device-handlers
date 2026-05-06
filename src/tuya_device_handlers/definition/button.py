"""Tuya button definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class ButtonDefinition:
    """Definition for a button entity."""

    button_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class ButtonQuirk(BaseEntityQuirk):
    """Quirk for a button entity."""

    definition_fn: Callable[
        [CustomerDevice],
        ButtonDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> ButtonDefinition | None:
    """Get the default button definition for a device."""
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return ButtonDefinition(button_wrapper=wrapper)
    return None
