"""Tests for vacuum definition."""

from tests import create_device
from tuya_device_handlers.definition.vacuum import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.device_wrapper.vacuum import (
    VacuumActionWrapper,
    VacuumActivityWrapper,
)


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("sd_i6hyjg3af7doaswm.json")
    assert (definition := get_default_definition(device))
    assert isinstance(definition.action_wrapper, VacuumActionWrapper)
    assert isinstance(definition.activity_wrapper, VacuumActivityWrapper)
    assert isinstance(definition.fan_speed_wrapper, DPCodeEnumWrapper)
