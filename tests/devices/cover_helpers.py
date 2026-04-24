"""Helpers for quirk cover tests."""

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.cover import (
    CoverDefinition,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.cover import (
    CoverInstructionSpecialEnumWrapper,
)


def _get_cl_cover_default_definitions(
    device: CustomerDevice,
) -> list[CoverDefinition | None]:
    """Get the default cover definition for a CL device."""
    return [
        get_default_definition(
            device,
            instruction_dpcode="control",
            current_state_dpcode=("situation_set", "control"),
            current_position_dpcode=("percent_state", "percent_control"),
            set_position_dpcode="percent_control",
        ),
        get_default_definition(
            device,
            instruction_dpcode="control_2",
            current_position_dpcode="percent_state_2",
            set_position_dpcode="percent_control_2",
        ),
        get_default_definition(
            device,
            instruction_dpcode="control_3",
            current_position_dpcode="percent_state_3",
            set_position_dpcode="percent_control_3",
        ),
        get_default_definition(
            device,
            instruction_dpcode="mach_operate",
            current_position_dpcode="position",
            set_position_dpcode="position",
            instruction_wrapper=CoverInstructionSpecialEnumWrapper,
        ),
        get_default_definition(
            device,
            instruction_dpcode="switch_1",
            current_position_dpcode="percent_control",
            set_position_dpcode="percent_control",
        ),
    ]


def get_cover_default_definitions(
    device: CustomerDevice,
) -> list[CoverDefinition]:
    """Get the default cover definition for a device."""
    values: list[CoverDefinition | None] = []
    if device.category == "cl":
        values.extend(_get_cl_cover_default_definitions(device))
    return [definition for definition in values if definition]
