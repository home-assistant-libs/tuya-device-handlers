"""Tuya valve definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper
from ..helpers.homeassistant import TuyaValveDeviceClass
from .base import BaseEntityQuirk


@dataclass
class TuyaValveDefinition:
    control_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class ValveQuirk(BaseEntityQuirk):
    """Quirk for a valve entity."""

    device_class: TuyaValveDeviceClass | None = None

    definition_fn: Callable[
        [CustomerDevice],
        TuyaValveDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaValveDefinition | None:
    if wrapper := DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaValveDefinition(control_wrapper=wrapper)
    return None
