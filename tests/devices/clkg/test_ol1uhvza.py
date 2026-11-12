"""Regression tests for the Tuya ol1uhvza cover position quirk."""

from unittest.mock import patch

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry
from tuya_device_handlers.type_information import IntegerTypeInformation
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)


def test_position_mapping_forward(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The quirk cancels the default inversion for forward-mode covers."""
    device = create_device("clkg_ol1uhvza.json")
    assert device.status["control_back_mode"] == "forward"
    device.status["percent_control"] = 90

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    write_wrapper = definitions["control"].set_position_wrapper
    assert read_wrapper is not None
    assert write_wrapper is not None
    assert read_wrapper.read_device_status(device) == 10
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 30}
    ]

    filled_quirks_registry.initialise_device_quirk(device)
    definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    write_wrapper = definitions["control"].set_position_wrapper
    assert read_wrapper is not None
    assert write_wrapper is not None
    assert read_wrapper.read_device_status(device) == 90
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 70}
    ]


def test_quirk_type_information(filled_quirks_registry: QuirksRegistry) -> None:
    """Only percent_control uses inverted type information."""
    device = create_device("clkg_ol1uhvza.json")
    filled_quirks_registry.initialise_device_quirk(device)
    type_information = IntegerTypeInformation.find_dpcode(
        device, "percent_control"
    )
    assert isinstance(type_information, InvertedIntegerTypeInformationEx)
