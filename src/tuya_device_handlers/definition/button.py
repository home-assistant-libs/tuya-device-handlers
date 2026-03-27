"""Tuya button definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper
from .base import BaseEntityQuirk


@dataclass
class TuyaButtonDefinition:
    button_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class ButtonQuirk(BaseEntityQuirk):
    """Quirk for a button entity."""

    definition_fn: Callable[
        [CustomerDevice],
        TuyaButtonDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaButtonDefinition | None:
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaButtonDefinition(button_wrapper=wrapper)
    return None
