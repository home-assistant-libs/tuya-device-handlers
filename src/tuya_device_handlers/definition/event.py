"""Tuya event definition."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeTypeInformationWrapper
from ..helpers.homeassistant import TuyaEventDeviceClass
from .base import BaseEntityQuirk


@dataclass
class TuyaEventDefinition:
    event_wrapper: DeviceWrapper[tuple[str, dict[str, Any] | None]]


@dataclass(kw_only=True)
class EventQuirk(BaseEntityQuirk):
    """Quirk for an event entity."""

    device_class: TuyaEventDeviceClass | None = None

    definition_fn: Callable[
        [CustomerDevice],
        TuyaEventDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    dpcode: str,
    wrapper_class: type[DPCodeTypeInformationWrapper],  # type: ignore[type-arg]
) -> TuyaEventDefinition | None:
    if wrapper := wrapper_class.find_dpcode(device, dpcode):
        return TuyaEventDefinition(
            event_wrapper=wrapper,
        )
    return None
