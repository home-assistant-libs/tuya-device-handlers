"""Tests for button definition."""

from tests import create_device
from tuya_device_handlers.definition.button import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition."""
    device = create_device("sd_lr33znaodtyarrrz.json")
    assert (definition := get_default_definition(device, "reset_duster_cloth"))
    assert isinstance(definition.button_wrapper, DPCodeBooleanWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition."""
    device = create_device("sd_lr33znaodtyarrrz.json")
    assert not get_default_definition(device, "bad")
