"""Tuya fan definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper, DPCodeEnumWrapper
from ..device_wrapper.fan import (
    FanDirectionEnumWrapper,
    FanSpeedEnumWrapper,
    FanSpeedIntegerWrapper,
)
from ..helpers.homeassistant import TuyaFanDirection
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class FanDefinition:
    direction_wrapper: DeviceWrapper[TuyaFanDirection] | None
    mode_wrapper: DeviceWrapper[str] | None
    oscillate_wrapper: DeviceWrapper[bool] | None
    speed_wrapper: DeviceWrapper[int] | None
    switch_wrapper: DeviceWrapper[bool] | None


# Deprecated alias for backward compatibility
TuyaFanDefinition = FanDefinition


@dataclass(kw_only=True)
class FanQuirk(BaseEntityQuirk):
    """Quirk for a fan entity."""

    definition_fn: Callable[
        [CustomerDevice],
        FanDefinition | None,
    ]


_DIRECTION_DPCODES = ("fan_direction",)
_MODE_DPCODES = ("fan_mode", "mode")
_OSCILLATE_DPCODES = ("switch_horizontal", "switch_vertical")
_SPEED_DPCODES = ("fan_speed_percent", "fan_speed", "speed", "fan_speed_enum")
_SWITCH_DPCODES = ("switch_fan", "fan_switch", "switch")


def get_default_definition(device: CustomerDevice) -> FanDefinition | None:
    properties_to_check: set[str] = {
        # Main control switch
        *_SWITCH_DPCODES,
        # Other properties
        *_SPEED_DPCODES,
        *_OSCILLATE_DPCODES,
        *_DIRECTION_DPCODES,
    }
    if not any(
        (
            code in device.function
            or code in device.status
            or code in device.status_range
        )
        for code in properties_to_check
    ):
        return None
    return FanDefinition(
        direction_wrapper=FanDirectionEnumWrapper.find_dpcode(
            device, _DIRECTION_DPCODES, prefer_function=True
        ),
        mode_wrapper=DPCodeEnumWrapper.find_dpcode(
            device, _MODE_DPCODES, prefer_function=True
        ),
        oscillate_wrapper=DPCodeBooleanWrapper.find_dpcode(
            device, _OSCILLATE_DPCODES, prefer_function=True
        ),
        speed_wrapper=FanSpeedIntegerWrapper.find_dpcode(
            device, _SPEED_DPCODES, prefer_function=True
        )
        or FanSpeedEnumWrapper.find_dpcode(
            device, _SPEED_DPCODES, prefer_function=True
        ),
        switch_wrapper=DPCodeBooleanWrapper.find_dpcode(
            device, _SWITCH_DPCODES, prefer_function=True
        ),
    )
