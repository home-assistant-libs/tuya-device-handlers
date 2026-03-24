"""Tests for switch definition."""

from tests import create_device
from tuya_device_handlers.definition.switch import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("cz_PGEkBctAbtzKOZng.json")
    assert (definition := get_default_definition(device, "switch"))
    assert isinstance(definition.switch_wrapper, DPCodeBooleanWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("cz_PGEkBctAbtzKOZng.json")
    assert not get_default_definition(device, "bad")
