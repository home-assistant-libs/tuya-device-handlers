"""Tests for device quirks."""

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition import cover as cover_definition
from tuya_device_handlers.device_wrapper.cover import (
    CoverClosedEnumWrapper,
    CoverInstructionEnumWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
)


def _get_cl_cover_default_definitions(
    device: CustomerDevice,
) -> list[cover_definition.CoverDefinition | None]:
    """Get the default cover definition for a CL device."""
    return [
        cover_definition.get_default_definition(
            device,
            current_position_dpcode=("percent_state", "percent_control"),
            current_state_dpcode=("situation_set", "control"),
            current_state_wrapper=CoverClosedEnumWrapper,
            instruction_dpcode="control",
            instruction_wrapper=CoverInstructionEnumWrapper,
            position_wrapper=DPCodeInvertedPercentageWrapper,
            set_position_dpcode="percent_control",
        )
    ]


def get_cover_default_definitions(
    device: CustomerDevice,
) -> list[cover_definition.CoverDefinition]:
    """Get the default cover definition for a device."""
    values: list[cover_definition.CoverDefinition | None] = []
    if device.category == "cl":
        values.extend(_get_cl_cover_default_definitions(device))
    return [definition for definition in values if definition]
