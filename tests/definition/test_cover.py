"""Tests for cover definition."""

from tests import create_device
from tuya_device_handlers.definition.cover import get_default_definition
from tuya_device_handlers.device_wrapper.cover import (
    CoverClosedEnumWrapper,
    CoverInstructionEnumWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
)


def test_get_default_definition() -> None:
    """Test get_default_definition."""
    device = create_device("cl_zah67ekd.json")
    assert (
        definition := get_default_definition(
            device,
            current_position_dpcode=("percent_state", "percent_control"),
            current_state_dpcode=("situation_set", "control"),
            instruction_dpcode="control",
            set_position_dpcode="percent_control",
            current_state_wrapper=CoverClosedEnumWrapper,
            instruction_wrapper=CoverInstructionEnumWrapper,
            position_wrapper=DPCodeInvertedPercentageWrapper,
        )
    )
    assert isinstance(
        definition.current_position_wrapper, DPCodeInvertedPercentageWrapper
    )
    assert isinstance(definition.current_state_wrapper, CoverClosedEnumWrapper)
    assert isinstance(
        definition.instruction_wrapper, CoverInstructionEnumWrapper
    )
    assert isinstance(
        definition.set_position_wrapper, DPCodeInvertedPercentageWrapper
    )
    assert not definition.tilt_position_wrapper


def test_get_default_definition_fails() -> None:
    """Test get_default_definition."""
    device = create_device("cl_zah67ekd.json")
    assert not get_default_definition(
        device,
        current_position_dpcode="bad",
        current_state_dpcode="bad",
        instruction_dpcode="bad",
        set_position_dpcode="bad",
        current_state_wrapper=CoverClosedEnumWrapper,
        instruction_wrapper=CoverInstructionEnumWrapper,
        position_wrapper=DPCodeInvertedPercentageWrapper,
    )
