"""Tuya number definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import DPCodeIntegerWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class NumberDefinition:
    """Definition for a number entity."""

    number_wrapper: DeviceWrapper[float]


@dataclass(kw_only=True)
class NumberQuirk(BaseEntityQuirk):
    """Quirk for a number entity."""

    definition_fn: Callable[
        [CustomerDevice],
        NumberDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> NumberDefinition | None:
    """Get the default number definition for a device."""
    if wrapper := DPCodeIntegerWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return NumberDefinition(number_wrapper=wrapper)
    return None
