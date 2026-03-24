"""Tests for humidifier definition."""

from tests import create_device
from tuya_device_handlers.definition.humidifier import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeRoundedIntegerWrapper,
)


def test_get_default_definition() -> None:
    """Test get_default_definition"""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert (
        definition := get_default_definition(
            device,
            switch_dpcode=("switch", "switch_spray"),
            current_humidity_dpcode="humidity_indoor",
            humidity_dpcode="dehumidity_set_value",
        )
    )
    assert isinstance(definition.switch_wrapper, DPCodeBooleanWrapper)
    assert isinstance(
        definition.current_humidity_wrapper, DPCodeRoundedIntegerWrapper
    )
    assert not (definition.target_humidity_wrapper)


def test_get_default_definition_fails() -> None:
    """Test get_default_definition"""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert not get_default_definition(
        device,
        switch_dpcode="bad",
        current_humidity_dpcode=None,
        humidity_dpcode=None,
    )
