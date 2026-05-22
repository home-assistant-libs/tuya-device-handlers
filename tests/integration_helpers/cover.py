"""Helpers for quirk cover tests.

The category mapping below mirrors the ``COVERS`` dictionary in Home
Assistant core, so tests can assert that a quirk produces the covers core
would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/cover.py
"""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.cover import (
    CoverDefinition,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.cover import (
    ControlBackModePercentageMappingWrapper,
    CoverClosedEnumWrapper,
    CoverInstructionEnumWrapper,
    CoverInstructionSpecialEnumWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedBooleanWrapper,
    DPCodeInvertedPercentageWrapper,
)

_WrapperClass = type[DPCodeTypeInformationWrapper]


@dataclass(frozen=True)
class CoverEntityDescription:
    """Describes a Tuya cover, mirroring the Home Assistant core mapping.

    ``key`` doubles as the instruction DPCode, as in Home Assistant core.
    """

    key: str
    current_position_dpcode: str | tuple[str, ...] | None = None
    current_state_dpcode: str | tuple[str, ...] | None = None
    set_position_dpcode: str | None = None
    current_state_wrapper: _WrapperClass = CoverClosedEnumWrapper
    instruction_wrapper: _WrapperClass = CoverInstructionEnumWrapper
    position_wrapper: _WrapperClass = DPCodeInvertedPercentageWrapper


_COVERS: dict[str, tuple[CoverEntityDescription, ...]] = {
    "ckmkzq": (
        CoverEntityDescription(
            key="switch_1",
            current_state_dpcode="doorcontact_state",
            current_state_wrapper=DPCodeInvertedBooleanWrapper,
        ),
        CoverEntityDescription(
            key="switch_2",
            current_state_dpcode="doorcontact_state_2",
            current_state_wrapper=DPCodeInvertedBooleanWrapper,
        ),
        CoverEntityDescription(
            key="switch_3",
            current_state_dpcode="doorcontact_state_3",
            current_state_wrapper=DPCodeInvertedBooleanWrapper,
        ),
    ),
    "cl": (
        CoverEntityDescription(
            key="control",
            current_position_dpcode=("percent_state", "percent_control"),
            current_state_dpcode=("situation_set", "control"),
            set_position_dpcode="percent_control",
        ),
        CoverEntityDescription(
            key="control_2",
            current_position_dpcode="percent_state_2",
            set_position_dpcode="percent_control_2",
        ),
        CoverEntityDescription(
            key="control_3",
            current_position_dpcode="percent_state_3",
            set_position_dpcode="percent_control_3",
        ),
        CoverEntityDescription(
            key="mach_operate",
            current_position_dpcode="position",
            set_position_dpcode="position",
            instruction_wrapper=CoverInstructionSpecialEnumWrapper,
        ),
        CoverEntityDescription(
            key="switch_1",
            current_position_dpcode="percent_control",
            set_position_dpcode="percent_control",
        ),
    ),
    "clkg": (
        CoverEntityDescription(
            key="control",
            current_position_dpcode="percent_control",
            set_position_dpcode="percent_control",
            position_wrapper=ControlBackModePercentageMappingWrapper,
        ),
        CoverEntityDescription(
            key="control_2",
            current_position_dpcode="percent_control_2",
            set_position_dpcode="percent_control_2",
            position_wrapper=ControlBackModePercentageMappingWrapper,
        ),
    ),
    "jdcljqr": (
        CoverEntityDescription(
            key="control",
            current_position_dpcode="percent_state",
            set_position_dpcode="percent_control",
        ),
    ),
}


def get_cover_default_definitions(
    device: CustomerDevice,
) -> dict[str, CoverDefinition]:
    """Get the default cover definitions Home Assistant builds for a device."""
    return {
        description.key: definition
        for description in _COVERS.get(device.category, ())
        if (
            definition := get_default_definition(
                device,
                instruction_dpcode=description.key,
                current_position_dpcode=description.current_position_dpcode,
                current_state_dpcode=description.current_state_dpcode,
                set_position_dpcode=description.set_position_dpcode,
                current_state_wrapper=description.current_state_wrapper,
                instruction_wrapper=description.instruction_wrapper,
                position_wrapper=description.position_wrapper,
            )
        )
    }
