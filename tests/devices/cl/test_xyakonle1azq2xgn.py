"""Quirk test for Tuya blind motor (product_id xyakonle1azq2xgn)."""

from unittest.mock import patch

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_removed_position(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, no position wrapper should exist."""
    device = create_device("cl_xyakonle1azq2xgn.json")
    device.status["percent_state"] = 0

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    wrapper = definitions["control"].set_position_wrapper
    assert wrapper is not None

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is None
    wrapper = definitions["control"].set_position_wrapper
    assert wrapper is None
