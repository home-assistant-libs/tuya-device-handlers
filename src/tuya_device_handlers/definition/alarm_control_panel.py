"""Tuya alarm control panel definition."""

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


@dataclass
class TuyaAlarmControlPanelDefinition:
    action_wrapper: DeviceWrapper[TuyaAlarmControlPanelAction]
    changed_by_wrapper: DeviceWrapper[str] | None
    state_wrapper: DeviceWrapper[TuyaAlarmControlPanelState]


def get_default_definition(
    device: CustomerDevice,
) -> TuyaAlarmControlPanelDefinition | None:
    if not (
        master_mode := EnumTypeInformation.find_dpcode(
            device, "master_mode", prefer_function=True
        )
    ):
        return None
    return TuyaAlarmControlPanelDefinition(
        action_wrapper=AlarmActionWrapper(master_mode.dpcode, master_mode),
        changed_by_wrapper=AlarmChangedByWrapper.find_dpcode(
            device, "alarm_msg"
        ),
        state_wrapper=AlarmStateWrapper(master_mode.dpcode, master_mode),
    )
