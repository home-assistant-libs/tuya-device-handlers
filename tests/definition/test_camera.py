"""Tests for camera definition."""

from tests import create_device
from tuya_device_handlers.definition.camera import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("sp_rudejjigkywujjvs.json")
    assert (definition := get_default_definition(device))
    assert isinstance(definition.motion_detection_switch, DPCodeBooleanWrapper)
    assert isinstance(definition.recording_status, DPCodeBooleanWrapper)
