"""Tuya number definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeIntegerWrapper
from ..helpers.homeassistant import TuyaNumberDeviceClass
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class NumberDefinition:
    number_wrapper: DeviceWrapper[float]


# Deprecated alias for backward compatibility
TuyaNumberDefinition = NumberDefinition


@dataclass(kw_only=True)
class NumberQuirk(BaseEntityQuirk):
    """Quirk for a number entity."""

    device_class: TuyaNumberDeviceClass | None = None

    definition_fn: Callable[
        [CustomerDevice],
        NumberDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> NumberDefinition | None:
    if wrapper := DPCodeIntegerWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return NumberDefinition(number_wrapper=wrapper)
    return None
