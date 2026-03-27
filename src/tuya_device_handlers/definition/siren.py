"""Tuya siren definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper
from .base import BaseEntityQuirk


@dataclass
class TuyaSirenDefinition:
    siren_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class SirenQuirk(BaseEntityQuirk):
    """Quirk for a siren entity."""

    definition_fn: Callable[
        [CustomerDevice],
        TuyaSirenDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaSirenDefinition | None:
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaSirenDefinition(siren_wrapper=wrapper)
    return None
