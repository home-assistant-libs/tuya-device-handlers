"""Tuya valve definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class ValveDefinition:
    """Definition for a valve entity."""

    control_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class ValveQuirk(BaseEntityQuirk):
    """Quirk for a valve entity."""

    definition_fn: Callable[
        [CustomerDevice],
        ValveDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> ValveDefinition | None:
    """Get the default valve definition for a device."""
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return ValveDefinition(control_wrapper=wrapper)
    return None
