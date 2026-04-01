"""Tuya sensor definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import (
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
    DPCodeTypeInformationWrapper,
)
from ..device_wrapper.sensor import DeltaIntegerWrapper
from ..helpers.homeassistant import TuyaSensorDeviceClass, TuyaSensorStateClass
from ..type_information import IntegerTypeInformation
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class SensorDefinition:
    sensor_wrapper: DeviceWrapper[str | int | float]


# Deprecated alias for backward compatibility
TuyaSensorDefinition = SensorDefinition


@dataclass(kw_only=True)
class SensorQuirk(BaseEntityQuirk):
    """Quirk for a sensor entity."""

    device_class: TuyaSensorDeviceClass | None = None
    state_class: TuyaSensorStateClass | None = None
    suggested_unit_of_measurement: str | None = None

    definition_fn: Callable[
        [CustomerDevice],
        SensorDefinition | None,
    ]


def get_default_definition(
    device: CustomerDevice,
    dpcode: str,
    wrapper_class: tuple[type[DPCodeTypeInformationWrapper], ...] | None = None,  # type: ignore[type-arg]
) -> SensorDefinition | None:
    """Get DPCode wrapper for an entity description."""
    if wrapper_class:
        for cls in wrapper_class:
            if wrapper := cls.find_dpcode(device, dpcode):
                return SensorDefinition(sensor_wrapper=wrapper)
        return None

    # Check for integer type first, using delta wrapper only for sum report_type
    if type_information := IntegerTypeInformation.find_dpcode(device, dpcode):
        if type_information.report_type == "sum":
            return SensorDefinition(
                sensor_wrapper=DeltaIntegerWrapper(  # type: ignore[arg-type]
                    type_information.dpcode, type_information
                )
            )
        return SensorDefinition(
            sensor_wrapper=DPCodeIntegerWrapper(
                type_information.dpcode, type_information
            )
        )

    if wrapper := DPCodeEnumWrapper.find_dpcode(device, dpcode):
        return SensorDefinition(sensor_wrapper=wrapper)  # type: ignore[arg-type]
    return None
