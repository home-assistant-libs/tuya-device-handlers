"""Tuya device wrapper."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..helpers.homeassistant import (
    TuyaAlarmControlPanelAction,
    TuyaAlarmControlPanelState,
)
from ..type_information import EnumTypeInformation
from .base import DeviceWrapper
from .common import DPCodeEnumWrapper, DPCodeRawWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


@dataclass
class TuyaAlarmControlPanelDefinition:
    action_wrapper: DeviceWrapper[TuyaAlarmControlPanelAction]
    changed_by_wrapper: DeviceWrapper[str] | None
    state_wrapper: DeviceWrapper[TuyaAlarmControlPanelState]


class AlarmChangedByWrapper(DPCodeRawWrapper[str]):
    """Wrapper for changed_by.

    Decode base64 to utf-16be string, but only if alarm has been triggered.
    """

    def read_device_status(self, device: CustomerDevice) -> str | None:
        """Read the device status."""
        if (
            device.status.get("master_state") != "alarm"
            or (status := self._read_dpcode_value(device)) is None
        ):
            return None
        return status.decode("utf-16be")


class AlarmStateWrapper(DPCodeEnumWrapper[TuyaAlarmControlPanelState]):
    """Wrapper for the alarm state of a device.

    Handles alarm mode enum values and determines the alarm state,
    including logic for detecting when the alarm is triggered and
    distinguishing triggered state from battery warnings.
    """

    _STATE_MAPPINGS = {
        # Tuya device mode => Home Assistant panel state
        "disarmed": TuyaAlarmControlPanelState.DISARMED,
        "arm": TuyaAlarmControlPanelState.ARMED_AWAY,
        "home": TuyaAlarmControlPanelState.ARMED_HOME,
        "sos": TuyaAlarmControlPanelState.TRIGGERED,
    }

    def read_device_status(
        self, device: CustomerDevice
    ) -> TuyaAlarmControlPanelState | None:
        """Read the device status."""
        # When the alarm is triggered, only its 'state' is changing. From 'normal' to 'alarm'.
        # The 'mode' doesn't change, and stays as 'arm' or 'home'.
        if device.status.get("master_state") == "alarm":
            # Only report as triggered if NOT a battery warning
            if not (
                (encoded_msg := device.status.get("alarm_msg"))
                and (
                    decoded_message := base64.b64decode(encoded_msg).decode(
                        "utf-16be"
                    )
                )
                and "Sensor Low Battery" in decoded_message
            ):
                return TuyaAlarmControlPanelState.TRIGGERED

        if (status := self._read_dpcode_value(device)) is None:
            return None
        return self._STATE_MAPPINGS.get(status)


class AlarmActionWrapper(DPCodeEnumWrapper[TuyaAlarmControlPanelAction]):
    """Wrapper for setting the alarm mode of a device."""

    _ACTION_MAPPINGS = {
        # Home Assistant action => Tuya device mode
        TuyaAlarmControlPanelAction.ARM_HOME: "home",
        TuyaAlarmControlPanelAction.ARM_AWAY: "arm",
        TuyaAlarmControlPanelAction.DISARM: "disarmed",
        TuyaAlarmControlPanelAction.TRIGGER: "sos",
    }

    def __init__(
        self, dpcode: str, type_information: EnumTypeInformation
    ) -> None:
        """Init _AlarmActionWrapper."""
        super().__init__(dpcode, type_information)
        self.options = [
            ha_action
            for ha_action, tuya_action in self._ACTION_MAPPINGS.items()
            if tuya_action in type_information.range
        ]

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> Any:
        """Convert value to raw value."""
        if value in self.options:
            return self._ACTION_MAPPINGS[value]
        raise ValueError(f"Unsupported value {value} for {self.dpcode}")
