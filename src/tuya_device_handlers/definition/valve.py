"""Tuya valve definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import (
    DPCodeBooleanWrapper,
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.extended import DPCodePercentageWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class ValveDefinition:
    """Definition for a valve entity."""

    control_wrapper: DeviceWrapper[bool]
    current_position_wrapper: DeviceWrapper[int] | None = None
    set_position_wrapper: DeviceWrapper[int] | None = None


@dataclass(kw_only=True)
class ValveQuirk(BaseEntityQuirk):
    """Quirk for a valve entity."""

    definition_fn: Callable[
        [CustomerDevice],
        ValveDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    dpcode: str,
    *,
    current_position_dpcode: str | tuple[str, ...] | None = None,
    set_position_dpcode: str | tuple[str, ...] | None = None,
    position_wrapper: type[
        DPCodeTypeInformationWrapper
    ] = DPCodePercentageWrapper,
) -> ValveDefinition | None:
    """Get the default valve definition for a device."""
    if not (
        control_wrapper := DPCodeBooleanWrapper.find_dpcode(
            device, dpcode, prefer_function=True
        )
    ):
        return None

    return ValveDefinition(
        control_wrapper=control_wrapper,
        current_position_wrapper=position_wrapper.find_dpcode(
            device, current_position_dpcode
        ),
        set_position_wrapper=position_wrapper.find_dpcode(
            device, set_position_dpcode, prefer_function=True
        ),
    )
