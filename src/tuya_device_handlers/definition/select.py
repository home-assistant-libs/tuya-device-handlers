"""Tuya select definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeEnumWrapper
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class SelectDefinition:
    select_wrapper: DeviceWrapper[str]


# Deprecated alias for backward compatibility
TuyaSelectDefinition = SelectDefinition


@dataclass(kw_only=True)
class SelectQuirk(BaseEntityQuirk):
    """Quirk for a select entity."""

    definition_fn: Callable[
        [CustomerDevice],
        SelectDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> SelectDefinition | None:
    if wrapper := DPCodeEnumWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return SelectDefinition(select_wrapper=wrapper)
    return None
