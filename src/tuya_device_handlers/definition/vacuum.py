"""Tuya vacuum definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.device_wrapper.vacuum import (
    VacuumActionWrapper,
    VacuumActivityWrapper,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaVacuumAction,
    TuyaVacuumActivity,
)

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class VacuumDefinition:
    """Definition for a vacuum entity."""

    action_wrapper: DeviceWrapper[TuyaVacuumAction] | None
    activity_wrapper: DeviceWrapper[TuyaVacuumActivity] | None
    fan_speed_wrapper: DeviceWrapper[str] | None


@dataclass(kw_only=True)
class VacuumQuirk(BaseEntityQuirk):
    """Quirk for a vacuum entity."""

    definition_fn: Callable[
        [CustomerDevice],
        VacuumDefinition | None,
    ]


def get_default_definition(device: CustomerDevice) -> VacuumDefinition:
    """Get the default vacuum definition for a device."""
    return VacuumDefinition(
        action_wrapper=VacuumActionWrapper.find_dpcode(device),
        activity_wrapper=VacuumActivityWrapper.find_dpcode(device),
        fan_speed_wrapper=DPCodeEnumWrapper.find_dpcode(
            device, "suction", prefer_function=True
        ),
    )
