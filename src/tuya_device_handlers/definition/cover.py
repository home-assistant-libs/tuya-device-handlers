"""Tuya cover definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeTypeInformationWrapper
from ..device_wrapper.cover import CoverInstructionBooleanWrapper
from ..helpers.homeassistant import TuyaCoverAction, TuyaCoverDeviceClass
from .base import BaseEntityQuirk


@dataclass
class TuyaCoverDefinition:
    current_position_wrapper: DeviceWrapper[int] | None
    current_state_wrapper: DeviceWrapper[bool] | None
    instruction_wrapper: DeviceWrapper[TuyaCoverAction] | None
    set_position_wrapper: DeviceWrapper[int] | None
    tilt_position_wrapper: DeviceWrapper[int] | None


@dataclass(kw_only=True)
class CoverQuirk(BaseEntityQuirk):
    """Quirk for a cover entity."""

    device_class: TuyaCoverDeviceClass | None = None

    definition_fn: Callable[
        [CustomerDevice],
        TuyaCoverDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    *,
    current_position_dpcode: str | tuple[str, ...] | None,
    current_state_dpcode: str | tuple[str, ...] | None,
    instruction_dpcode: str,
    set_position_dpcode: str | None,
    current_state_wrapper: type[DPCodeTypeInformationWrapper],  # type: ignore[type-arg]
    instruction_wrapper: type[DPCodeTypeInformationWrapper],  # type: ignore[type-arg]
    position_wrapper: type[DPCodeTypeInformationWrapper],  # type: ignore[type-arg]
) -> TuyaCoverDefinition | None:
    if not (
        instruction_dpcode in device.function
        or instruction_dpcode in device.status_range
    ):
        return None

    return TuyaCoverDefinition(
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
