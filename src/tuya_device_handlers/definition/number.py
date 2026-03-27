"""Tuya number definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeIntegerWrapper
from ..helpers.homeassistant import TuyaNumberDeviceClass
from .base import BaseEntityQuirk


@dataclass
class TuyaNumberDefinition:
    number_wrapper: DeviceWrapper[float]


@dataclass(kw_only=True)
class NumberQuirk(BaseEntityQuirk):
    """Quirk for a number entity."""

    device_class: TuyaNumberDeviceClass | None = None

    definition_fn: Callable[
        [CustomerDevice],
        TuyaNumberDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice, dpcode: str
) -> TuyaNumberDefinition | None:
    if wrapper := DPCodeIntegerWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    ):
        return TuyaNumberDefinition(number_wrapper=wrapper)
    return None
