"""Tuya switch definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper
from ..helpers.homeassistant import TuyaSwitchDeviceClass
from .base import BaseEntityQuirk


@dataclass
class TuyaSwitchDefinition:
    switch_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class SwitchQuirk(BaseEntityQuirk):
    """Definition for a switch entity."""

    device_class: TuyaSwitchDeviceClass | None = None

    definition_fn: Callable[
        [CustomerDevice],
        TuyaSwitchDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaSwitchDefinition | None:
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaSwitchDefinition(switch_wrapper=wrapper)
    return None
