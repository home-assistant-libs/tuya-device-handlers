"""Tuya vacuum definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeEnumWrapper
from ..device_wrapper.vacuum import VacuumActionWrapper, VacuumActivityWrapper
from ..helpers.homeassistant import TuyaVacuumAction, TuyaVacuumActivity
from .base import BaseEntityQuirk


@dataclass
class TuyaVacuumDefinition:
    action_wrapper: DeviceWrapper[TuyaVacuumAction] | None
    activity_wrapper: DeviceWrapper[TuyaVacuumActivity] | None
    fan_speed_wrapper: DeviceWrapper[str] | None


@dataclass(kw_only=True)
class VacuumQuirk(BaseEntityQuirk):
    """Quirk for a vacuum entity."""

    definition_fn: Callable[
        [CustomerDevice],
        TuyaVacuumDefinition | None,
    ]


def get_default_definition(device: CustomerDevice) -> TuyaVacuumDefinition:
    return TuyaVacuumDefinition(
        action_wrapper=VacuumActionWrapper.find_dpcode(device),
        activity_wrapper=VacuumActivityWrapper.find_dpcode(device),
        fan_speed_wrapper=DPCodeEnumWrapper.find_dpcode(
            device, "suction", prefer_function=True
        ),
    )
