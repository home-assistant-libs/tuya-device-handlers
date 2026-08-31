"""Tests for the nfq1essvr99qsvvd cover position quirk.

This device (Canisteo Smart Zebra Shades) reports and accepts position in
HA convention (0=closed, 100=open). Without the quirk the default
DPCodeInvertedPercentageWrapper incorrectly inverts position values in
both directions.

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
    """With quirk, percent_state=95 reads as 95 (not inverted to 5)."""
    device = create_device("cl_nfq1essvr99qsvvd.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 5

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 95


def test_quirk_corrects_position_write(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk pre-inverts percent_control so writes use HA convention.

    Without the quirk the default wrapper inverts position 70 into raw 30;
    with the quirk the pre-inversion cancels out and raw 70 is sent.
    """
    device = create_device("cl_nfq1essvr99qsvvd.json")

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
