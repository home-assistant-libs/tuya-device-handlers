"""Tuya binary sensor definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.binary_sensor import (
    DPCodeBitmapBitWrapper,
    DPCodeInSetWrapper,
)
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class BinarySensorDefinition:
    """Definition for a binary sensor entity."""

    binary_sensor_wrapper: DeviceWrapper[bool]


@dataclass(kw_only=True)
class BinarySensorQuirk(BaseEntityQuirk):
    """Quirk for a binary sensor entity."""

    definition_fn: Callable[
        [CustomerDevice],
        BinarySensorDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    dpcode: str,
    bitmap_key: str | None = None,
    on_value: bool | float | int | str | set[bool | float | int | str] = True,
) -> BinarySensorDefinition | None:
    """Get the default binary sensor definition for a device."""
    if bitmap_key is not None:
        if bitmap_wrapper := DPCodeBitmapBitWrapper.find_dpcode(
            device, dpcode, bitmap_key=bitmap_key
        ):
            return BinarySensorDefinition(binary_sensor_wrapper=bitmap_wrapper)
        return None

    if bool_type := DPCodeBooleanWrapper.find_dpcode(device, dpcode):
        return BinarySensorDefinition(binary_sensor_wrapper=bool_type)

    # Legacy / compatibility
    if dpcode not in device.status:
        return None
    return BinarySensorDefinition(
        binary_sensor_wrapper=DPCodeInSetWrapper(
            dpcode,
            on_value if isinstance(on_value, set) else {on_value},
        )
    )
