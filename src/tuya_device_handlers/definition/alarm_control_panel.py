"""Tuya alarm control panel definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.alarm_control_panel import (
    AlarmActionWrapper,
    AlarmChangedByWrapper,
    AlarmStateWrapper,
)
from ..helpers.homeassistant import (
    TuyaAlarmControlPanelAction,
    TuyaAlarmControlPanelState,
)
from ..type_information import EnumTypeInformation
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class AlarmControlPanelDefinition:
    action_wrapper: DeviceWrapper[TuyaAlarmControlPanelAction]
    changed_by_wrapper: DeviceWrapper[str] | None
    state_wrapper: DeviceWrapper[TuyaAlarmControlPanelState]


# Deprecated alias for backward compatibility
TuyaAlarmControlPanelDefinition = AlarmControlPanelDefinition


@dataclass(kw_only=True)
class AlarmControlPanelQuirk(BaseEntityQuirk):
    """Quirk for an alarm control panel entity."""

    definition_fn: Callable[
        [CustomerDevice],
        AlarmControlPanelDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
) -> AlarmControlPanelDefinition | None:
    if not (
        master_mode := EnumTypeInformation.find_dpcode(
            device, "master_mode", prefer_function=True
        )
    ):
        return None
    return AlarmControlPanelDefinition(
        action_wrapper=AlarmActionWrapper(master_mode.dpcode, master_mode),
        changed_by_wrapper=AlarmChangedByWrapper.find_dpcode(
            device, "alarm_msg"
        ),
        state_wrapper=AlarmStateWrapper(master_mode.dpcode, master_mode),
    )
