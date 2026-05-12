"""Tests for siren definition."""

from tests import create_device
from tuya_device_handlers.definition.siren import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition."""
    device = create_device("sp_sdd5f5f2dl5wydjf.json")
    assert (definition := get_default_definition(device, "siren_switch"))
    assert isinstance(definition.siren_wrapper, DPCodeBooleanWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition."""
    device = create_device("sp_sdd5f5f2dl5wydjf.json")
    assert not get_default_definition(device, "bad")
