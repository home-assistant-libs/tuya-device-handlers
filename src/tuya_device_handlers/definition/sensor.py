"""Tuya sensor definition."""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import (
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
    DPCodeTypeInformationWrapper,
)
from ..device_wrapper.sensor import DeltaIntegerWrapper
from ..type_information import IntegerTypeInformation


@dataclass
class TuyaSensorDefinition:
    sensor_wrapper: DeviceWrapper[str | int | float]


def get_default_definition(
    device: CustomerDevice,
    dpcode: str,
    wrapper_class: tuple[type[DPCodeTypeInformationWrapper], ...] | None,  # type: ignore[type-arg]
) -> TuyaSensorDefinition | None:
    """Get DPCode wrapper for an entity description."""
    if wrapper_class:
        for cls in wrapper_class:
            if wrapper := cls.find_dpcode(device, dpcode):
                return TuyaSensorDefinition(sensor_wrapper=wrapper)
        return None

    # Check for integer type first, using delta wrapper only for sum report_type
    if type_information := IntegerTypeInformation.find_dpcode(device, dpcode):
        if type_information.report_type == "sum":
            return TuyaSensorDefinition(
                sensor_wrapper=DeltaIntegerWrapper(  # type: ignore[arg-type]
                    type_information.dpcode, type_information
                )
            )
        return TuyaSensorDefinition(
            sensor_wrapper=DPCodeIntegerWrapper(
                type_information.dpcode, type_information
            )
        )

    if wrapper := DPCodeEnumWrapper.find_dpcode(device, dpcode):
        return TuyaSensorDefinition(sensor_wrapper=wrapper)  # type: ignore[arg-type]
    return None
