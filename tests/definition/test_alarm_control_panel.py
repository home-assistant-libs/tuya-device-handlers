"""Tests for alarm control panel definition."""

from tests import create_device
from tuya_device_handlers.definition.alarm_control_panel import (
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.alarm_control_panel import (
    AlarmActionWrapper,
    AlarmChangedByWrapper,
    AlarmStateWrapper,
)


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("mal_gyitctrjj1kefxp2.json")
    assert (definition := get_default_definition(device))
    assert isinstance(definition.action_wrapper, AlarmActionWrapper)
    assert isinstance(definition.changed_by_wrapper, AlarmChangedByWrapper)
    assert isinstance(definition.state_wrapper, AlarmStateWrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("sfkzq_ed7frwissyqrejic.json")
    assert not get_default_definition(device)
