"""Tests for the ethhg596wzx6nex2 cover position quirk."""

from unittest.mock import patch

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_corrects_position(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With the quirk, a nearly closed curtain remains nearly closed."""
    device = create_device("cl_ethhg596wzx6nex2.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 98

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 2


def test_quirk_corrects_position_write(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With the quirk, requested positions are sent without inversion."""
    device = create_device("cl_ethhg596wzx6nex2.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].set_position_wrapper
    assert wrapper is not None
    assert wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 30}
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].set_position_wrapper
    assert wrapper is not None
    assert wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 70}
    ]
