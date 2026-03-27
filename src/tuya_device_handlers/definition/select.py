"""Tuya select definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeEnumWrapper
from .base import BaseEntityQuirk


@dataclass
class TuyaSelectDefinition:
    select_wrapper: DeviceWrapper[str]


@dataclass(kw_only=True)
class SelectQuirk(BaseEntityQuirk):
    """Quirk for a select entity."""

    definition_fn: Callable[
        [CustomerDevice],
        TuyaSelectDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaSelectDefinition | None:
    if wrapper := DPCodeEnumWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaSelectDefinition(select_wrapper=wrapper)
    return None
