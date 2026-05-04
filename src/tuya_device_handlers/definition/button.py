"""Tuya button definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class ButtonDefinition:
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
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return ButtonDefinition(button_wrapper=wrapper)
    return None
