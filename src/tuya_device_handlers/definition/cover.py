"""Tuya cover definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.cover import (
    CoverClosedEnumWrapper,
    CoverInstructionBooleanWrapper,
    CoverInstructionEnumWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
)
from tuya_device_handlers.helpers.homeassistant import TuyaCoverAction

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class CoverDefinition:
    """Definition for a cover entity."""

    current_position_wrapper: DeviceWrapper[int] | None
    current_state_wrapper: DeviceWrapper[bool] | None
    instruction_wrapper: DeviceWrapper[TuyaCoverAction] | None
    set_position_wrapper: DeviceWrapper[int] | None
    tilt_position_wrapper: DeviceWrapper[int] | None


@dataclass(kw_only=True)
class CoverQuirk(BaseEntityQuirk):
    """Quirk for a cover entity."""

    definition_fn: Callable[
        [CustomerDevice],
        CoverDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    *,
    current_position_dpcode: str | tuple[str, ...] | None = None,
    current_state_dpcode: str | tuple[str, ...] | None = None,
    instruction_dpcode: str,
    set_position_dpcode: str | None = None,
    current_state_wrapper: type[
        DPCodeTypeInformationWrapper
    ] = CoverClosedEnumWrapper,
    instruction_wrapper: type[
        DPCodeTypeInformationWrapper
    ] = CoverInstructionEnumWrapper,
    position_wrapper: type[
        DPCodeTypeInformationWrapper
    ] = DPCodeInvertedPercentageWrapper,
) -> CoverDefinition | None:
    """Get the default cover definition for a device."""
    if not (
        instruction_dpcode in device.function
        or instruction_dpcode in device.status_range
    ):
        return None

    return CoverDefinition(
        current_position_wrapper=position_wrapper.find_dpcode(
            device, current_position_dpcode
        ),
        current_state_wrapper=current_state_wrapper.find_dpcode(
            device, current_state_dpcode
        ),
        instruction_wrapper=instruction_wrapper.find_dpcode(
            device, instruction_dpcode, prefer_function=True
        )
        or CoverInstructionBooleanWrapper.find_dpcode(
            device, instruction_dpcode, prefer_function=True
        ),
        set_position_wrapper=position_wrapper.find_dpcode(
            device, set_position_dpcode, prefer_function=True
        ),
        tilt_position_wrapper=position_wrapper.find_dpcode(
            device, ("angle_horizontal", "angle_vertical"), prefer_function=True
        ),
    )
