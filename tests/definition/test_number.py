"""Tests for number definition."""

from tests import create_device
from tuya_device_handlers.definition.number import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeIntegerWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("mal_gyitctrjj1kefxp2.json")
    assert (definition := get_default_definition(device, "delay_set"))
    assert isinstance(definition.number_wrapper, DPCodeIntegerWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("mal_gyitctrjj1kefxp2.json")
    assert not get_default_definition(device, "bad")
