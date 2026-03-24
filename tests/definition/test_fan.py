"""Tests for fan definition."""

from tests import create_device
from tuya_device_handlers.definition.fan import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert (definition := get_default_definition(device))
    assert isinstance(definition.switch_wrapper, DPCodeBooleanWrapper)
    assert not definition.direction_wrapper
    assert not definition.mode_wrapper
    assert not definition.speed_wrapper
    assert not definition.oscillate_wrapper


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert not get_default_definition(device)
