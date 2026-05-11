"""Tuya event definition."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.event import SimpleEventEnumWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class EventDefinition:
    """Definition for an event entity."""

    event_wrapper: DeviceWrapper[tuple[str, dict[str, Any] | None]]


@dataclass(kw_only=True)
class EventQuirk(BaseEntityQuirk):
    """Quirk for an event entity."""

    definition_fn: Callable[
        [CustomerDevice],
        EventDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    dpcode: str,
    wrapper_class: type[DPCodeTypeInformationWrapper] = SimpleEventEnumWrapper,
) -> EventDefinition | None:
    """Get the default event definition for a device."""
    if wrapper := wrapper_class.find_dpcode(device, dpcode):
        return EventDefinition(
            event_wrapper=wrapper,
        )
    return None
