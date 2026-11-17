"""Test the <device> cover position quirk."""

from unittest.mock import patch

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_corrects_position(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With the quirk, a position of 25 reads as 25 and is written as is."""
    device = create_device("cl_vexa5o82.json")
    device.status["percent_state"] = 25

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    assert read_wrapper is not None
    assert read_wrapper.read_device_status(device) == 75

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    write_wrapper = definitions["control"].set_position_wrapper
    assert read_wrapper is not None
    assert write_wrapper is not None
    assert read_wrapper.read_device_status(device) == 25
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 70}
    ]
