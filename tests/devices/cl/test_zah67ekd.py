"""Tests for the zah67ekd cover position quirk.

AM43拉绳电機-Zigbee (product_id zah67ekd) reports percent_state in HA
convention (0=closed, 100=open).  Without the quirk the default
DPCodeInvertedPercentageWrapper incorrectly inverts position values.

See https://github.com/home-assistant/core/issues/159800.
"""

from unittest.mock import patch

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_corrects_position(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, percent_state=52 reads as 52 (not inverted to 48)."""
    device = create_device("cl_zah67ekd.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 48

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 52


def test_quirk_corrects_position_write(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, setting position 70 sends raw value 70 (not 30)."""
    device = create_device("cl_zah67ekd.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.get_update_commands(device, 70) == [
        {"code": "percent_state", "value": 30}
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.get_update_commands(device, 70) == [
        {"code": "percent_state", "value": 70}
    ]
