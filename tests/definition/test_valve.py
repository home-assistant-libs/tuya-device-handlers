"""Tests for valve definition."""

from tests import create_device
from tuya_device_handlers.definition.valve import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert (definition := get_default_definition(device, "switch_1"))
    assert isinstance(definition.control_wrapper, DPCodeBooleanWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert not get_default_definition(device, "bad")
