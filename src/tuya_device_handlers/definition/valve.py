"""Tuya valve definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class ValveDefinition:
    control_wrapper: DeviceWrapper[bool]


# Deprecated alias for backward compatibility
TuyaValveDefinition = ValveDefinition


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
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return ValveDefinition(control_wrapper=wrapper)
    return None
