"""Definitions for alarm control panel entity."""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper
from ..helpers.homeassistant import (
    TuyaAlarmControlPanelAction,
    TuyaAlarmControlPanelState,
)


@dataclass
class TuyaAlarmControlPanelDefinition:
    action_wrapper: DeviceWrapper[TuyaAlarmControlPanelAction]
    changed_by_wrapper: DeviceWrapper[str] | None
    state_wrapper: DeviceWrapper[TuyaAlarmControlPanelState]
