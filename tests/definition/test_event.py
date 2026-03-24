"""Tests for event definition."""

from tests import create_device
from tuya_device_handlers.definition.event import get_default_definition
from tuya_device_handlers.device_wrapper.event import (
    Base64Utf8RawEventWrapper,
    SimpleEventEnumWrapper,
)


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("sp_sdd5f5f2dl5wydjf.json")
    assert (
        definition := get_default_definition(
            device, "doorbell_pic", Base64Utf8RawEventWrapper
        )
    )
    assert isinstance(definition.event_wrapper, Base64Utf8RawEventWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("sp_sdd5f5f2dl5wydjf.json")
    assert not get_default_definition(device, "bad", SimpleEventEnumWrapper)
