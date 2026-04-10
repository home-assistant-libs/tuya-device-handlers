"""Tuya event definition."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tuya_sharing import CustomerDevice

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeTypeInformationWrapper
from ..device_wrapper.event import SimpleEventEnumWrapper
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class EventDefinition:
    event_wrapper: DeviceWrapper[tuple[str, dict[str, Any] | None]]


# Deprecated alias for backward compatibility
TuyaEventDefinition = EventDefinition


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
    wrapper_class: type[DPCodeTypeInformationWrapper] = SimpleEventEnumWrapper,  # type: ignore[type-arg]
) -> EventDefinition | None:
    if wrapper := wrapper_class.find_dpcode(device, dpcode):
        return EventDefinition(
            event_wrapper=wrapper,
        )
    return None
