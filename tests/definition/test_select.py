"""Tests for select definition."""

from tests import create_device
from tuya_device_handlers.definition.select import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("cl_zah67ekd.json")
    assert (definition := get_default_definition(device, "control_back_mode"))
    assert isinstance(definition.select_wrapper, DPCodeEnumWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("cl_zah67ekd.json")
    assert not get_default_definition(device, "bad")
