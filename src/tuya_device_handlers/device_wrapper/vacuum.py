"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from ..helpers.homeassistant import TuyaVacuumAction, TuyaVacuumActivity
from .base import DeviceWrapper
from .common import DPCodeBooleanWrapper, DPCodeEnumWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class VacuumActivityWrapper(DeviceWrapper[TuyaVacuumActivity]):
    """Wrapper for the state of a vacuum."""

    _TUYA_STATUS_TO_HA = {
        "charge_done": TuyaVacuumActivity.DOCKED,
        "chargecompleted": TuyaVacuumActivity.DOCKED,
        "chargego": TuyaVacuumActivity.DOCKED,
        "charging": TuyaVacuumActivity.DOCKED,
        "cleaning": TuyaVacuumActivity.CLEANING,
        "docking": TuyaVacuumActivity.RETURNING,
        "goto_charge": TuyaVacuumActivity.RETURNING,
        "goto_pos": TuyaVacuumActivity.CLEANING,
        "mop_clean": TuyaVacuumActivity.CLEANING,
        "part_clean": TuyaVacuumActivity.CLEANING,
        "paused": TuyaVacuumActivity.PAUSED,
        "pick_zone_clean": TuyaVacuumActivity.CLEANING,
        "pos_arrived": TuyaVacuumActivity.CLEANING,
        "pos_unarrive": TuyaVacuumActivity.CLEANING,
        "random": TuyaVacuumActivity.CLEANING,
        "sleep": TuyaVacuumActivity.IDLE,
        "smart_clean": TuyaVacuumActivity.CLEANING,
        "smart": TuyaVacuumActivity.CLEANING,
        "spot_clean": TuyaVacuumActivity.CLEANING,
        "standby": TuyaVacuumActivity.IDLE,
        "wall_clean": TuyaVacuumActivity.CLEANING,
        "wall_follow": TuyaVacuumActivity.CLEANING,
        "zone_clean": TuyaVacuumActivity.CLEANING,
    }

    def __init__(
        self,
        pause_wrapper: DPCodeBooleanWrapper | None = None,
        status_wrapper: DPCodeEnumWrapper | None = None,
    ) -> None:
        """Init _VacuumActivityWrapper."""
        self._pause_wrapper = pause_wrapper
        self._status_wrapper = status_wrapper

    @classmethod
    def find_dpcode(cls, device: CustomerDevice) -> Self | None:
        """Find and return a _VacuumActivityWrapper for the given DP codes."""
        pause_wrapper = DPCodeBooleanWrapper.find_dpcode(device, "pause")
        status_wrapper = DPCodeEnumWrapper.find_dpcode(device, "status")
        if pause_wrapper or status_wrapper:
            return cls(
                pause_wrapper=pause_wrapper, status_wrapper=status_wrapper
            )
        return None

    def read_device_status(
        self, device: CustomerDevice
    ) -> TuyaVacuumActivity | None:
        """Read the device status."""
        if (
            self._status_wrapper
            and (status := self._status_wrapper.read_device_status(device))
            is not None
        ):
            return self._TUYA_STATUS_TO_HA.get(status)

        if self._pause_wrapper and self._pause_wrapper.read_device_status(
            device
        ):
            return TuyaVacuumActivity.PAUSED
        return None


class VacuumActionWrapper(DeviceWrapper[TuyaVacuumAction]):
    """Wrapper for sending actions to a vacuum."""

    _TUYA_MODE_RETURN_HOME = "chargego"

    def __init__(
        self,
        charge_wrapper: DPCodeBooleanWrapper | None,
        locate_wrapper: DPCodeBooleanWrapper | None,
        pause_wrapper: DPCodeBooleanWrapper | None,
        mode_wrapper: DPCodeEnumWrapper | None,
        switch_wrapper: DPCodeBooleanWrapper | None,
    ) -> None:
        """Init _VacuumActionWrapper."""
        self._charge_wrapper = charge_wrapper
        self._locate_wrapper = locate_wrapper
        self._mode_wrapper = mode_wrapper
        self._switch_wrapper = switch_wrapper

        self.options = []
        if charge_wrapper or (
            mode_wrapper and self._TUYA_MODE_RETURN_HOME in mode_wrapper.options
        ):
            self.options.append("return_to_base")
        if locate_wrapper:
            self.options.append("locate")
        if pause_wrapper:
            self.options.append("pause")
        if switch_wrapper:
            self.options.append("start")
            self.options.append("stop")

    @classmethod
    def find_dpcode(cls, device: CustomerDevice) -> Self:
        """Find and return a _VacuumActionWrapper for the given DP codes."""
        return cls(
            charge_wrapper=DPCodeBooleanWrapper.find_dpcode(
                device, "switch_charge", prefer_function=True
            ),
            locate_wrapper=DPCodeBooleanWrapper.find_dpcode(
                device, "seek", prefer_function=True
            ),
            mode_wrapper=DPCodeEnumWrapper.find_dpcode(
                device, "mode", prefer_function=True
            ),
            pause_wrapper=DPCodeBooleanWrapper.find_dpcode(device, "pause"),
            switch_wrapper=DPCodeBooleanWrapper.find_dpcode(
                device, "power_go", prefer_function=True
            ),
        )

    def get_update_commands(
        self, device: CustomerDevice, value: TuyaVacuumAction
    ) -> list[dict[str, Any]]:
        """Get the commands for the action wrapper."""
        if value == TuyaVacuumAction.LOCATE and self._locate_wrapper:
            return self._locate_wrapper.get_update_commands(device, True)
        if value == TuyaVacuumAction.PAUSE and self._switch_wrapper:
            return self._switch_wrapper.get_update_commands(device, False)
        if value == TuyaVacuumAction.RETURN_TO_BASE:
            if self._charge_wrapper:
                return self._charge_wrapper.get_update_commands(device, True)
            if self._mode_wrapper:
                return self._mode_wrapper.get_update_commands(
                    device, self._TUYA_MODE_RETURN_HOME
                )
        if value == TuyaVacuumAction.START and self._switch_wrapper:
            return self._switch_wrapper.get_update_commands(device, True)
        if value == TuyaVacuumAction.STOP and self._switch_wrapper:
            return self._switch_wrapper.get_update_commands(device, False)
        return []
