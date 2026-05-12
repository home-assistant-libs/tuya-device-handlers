"""Tuya siren definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class SirenDefinition:
    """Definition for a siren entity."""

    siren_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class SirenQuirk(BaseEntityQuirk):
    """Quirk for a siren entity."""

    definition_fn: Callable[
        [CustomerDevice],
        SirenDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> SirenDefinition | None:
    """Get the default siren definition for a device."""
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return SirenDefinition(siren_wrapper=wrapper)
    return None
