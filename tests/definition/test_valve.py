"""Tests for valve definition."""

from tests import create_device
from tuya_device_handlers.definition.valve import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper
from tuya_device_handlers.device_wrapper.extended import DPCodePercentageWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition."""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert (definition := get_default_definition(device, "switch_1"))
    assert isinstance(definition.control_wrapper, DPCodeBooleanWrapper)
    assert definition.current_position_wrapper is None
    assert definition.set_position_wrapper is None


def test_get_default_definition_fails() -> None:
    """Test get_default_definition."""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert not get_default_definition(device, "bad")


def test_get_default_definition_with_position() -> None:
    """Test get_default_definition for a valve reporting its position."""
    device = create_device("sfkzq_kcdiut0eqeni7b8n.json")
    assert (
        definition := get_default_definition(
            device,
            "switch",
            current_position_dpcode="percent_state",
            set_position_dpcode="percent_control",
        )
    )
    assert isinstance(definition.control_wrapper, DPCodeBooleanWrapper)
    assert isinstance(
        definition.current_position_wrapper, DPCodePercentageWrapper
    )
    assert isinstance(definition.set_position_wrapper, DPCodePercentageWrapper)


def test_get_default_definition_unknown_position() -> None:
    """Test unknown position dpcodes resolve to None."""
    device = create_device("sfkzq_kcdiut0eqeni7b8n.json")
    assert (
        definition := get_default_definition(
            device,
            "switch",
            current_position_dpcode="bad",
            set_position_dpcode="bad",
        )
    )
    assert definition.current_position_wrapper is None
    assert definition.set_position_wrapper is None
