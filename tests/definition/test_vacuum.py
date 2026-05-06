"""Tests for vacuum definition."""

from tests import create_device
from tuya_device_handlers.definition.vacuum import get_default_definition
from tuya_device_handlers.device_wrapper.vacuum import VacuumActionWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition."""
    device = create_device("sd_i6hyjg3af7doaswm.json")
    assert (definition := get_default_definition(device))
    assert isinstance(definition.action_wrapper, VacuumActionWrapper)
    assert not definition.activity_wrapper
    assert not definition.fan_speed_wrapper
