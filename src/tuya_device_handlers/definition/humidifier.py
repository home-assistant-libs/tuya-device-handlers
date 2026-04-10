"""Tuya humidifier definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import DPCodeBooleanWrapper, DPCodeEnumWrapper
from ..device_wrapper.extended import DPCodeRoundedIntegerWrapper
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class HumidifierDefinition:
    current_humidity_wrapper: DeviceWrapper[int] | None = None
    mode_wrapper: DeviceWrapper[str] | None = None
    switch_wrapper: DeviceWrapper[bool] | None = None
    target_humidity_wrapper: DeviceWrapper[int] | None = None


# Deprecated alias for backward compatibility
TuyaHumidifierDefinition = HumidifierDefinition


@dataclass(kw_only=True)
class HumidifierQuirk(BaseEntityQuirk):
    """Quirk for a humidifier entity."""

    definition_fn: Callable[
        [CustomerDevice],
        HumidifierDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    *,
    switch_dpcode: str | tuple[str, ...],
    current_humidity_dpcode: str | None = None,
    humidity_dpcode: str | None = None,
) -> HumidifierDefinition | None:
    properties_to_check: set[str | None] = {
        # Main control switch
        *(
            switch_dpcode
            if isinstance(switch_dpcode, tuple)
            else (switch_dpcode,)
        ),
        # Other humidity properties
        current_humidity_dpcode,
        humidity_dpcode,
    }
    if not any(
        (
            code in device.function
            or code in device.status
            or code in device.status_range
        )
        for code in properties_to_check
        if code is not None
    ):
        return None
    return HumidifierDefinition(
        current_humidity_wrapper=DPCodeRoundedIntegerWrapper.find_dpcode(
            device, current_humidity_dpcode
        ),
        mode_wrapper=DPCodeEnumWrapper.find_dpcode(
            device, "mode", prefer_function=True
        ),
        switch_wrapper=DPCodeBooleanWrapper.find_dpcode(
            device, switch_dpcode, prefer_function=True
        ),
        target_humidity_wrapper=DPCodeRoundedIntegerWrapper.find_dpcode(
            device, humidity_dpcode, prefer_function=True
        ),
    )
