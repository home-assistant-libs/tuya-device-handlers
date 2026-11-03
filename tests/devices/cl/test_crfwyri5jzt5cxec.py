"""Tests for the crfwyri5jzt5cxec cover position quirk.

This device (ZM25RW01) reports and accepts position in HA convention
(0=closed, 100=open) while control_back_mode is "back". Without the quirk
the default DPCodeInvertedPercentageWrapper incorrectly inverts position
values in both directions.
"""

from unittest.mock import patch

import pytest

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


@pytest.mark.parametrize(
    ("percent_state", "default_position", "quirk_position"),
    [
        (0, 100, 0),
        (25, 75, 25),
        (100, 0, 100),
    ],
)
def test_quirk_corrects_position(
    filled_quirks_registry: QuirksRegistry,
    percent_state: int,
    default_position: int,
    quirk_position: int,
) -> None:
    """With quirk, percent_state is reported as is (not inverted)."""
    device = create_device("cl_crfwyri5jzt5cxec.json")
    assert device.status["control_back_mode"] == "back"
    device.status["percent_state"] = percent_state

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == default_position

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == quirk_position


def test_quirk_corrects_position_write(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk pre-inverts percent_control so writes use HA convention.

    Without the quirk the default wrapper inverts position 70 into raw 30;
    with the quirk the pre-inversion cancels out and raw 70 is sent.
    """
    device = create_device("cl_crfwyri5jzt5cxec.json")

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
