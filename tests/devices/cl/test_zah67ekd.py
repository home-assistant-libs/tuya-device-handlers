"""Tests for the zah67ekd per-device cover position quirk.

This device reports position in the standard HA convention (0=closed,
100=open). Without the quirk the default DPCodeInvertedPercentageWrapper
incorrectly flips position values.

See https://github.com/home-assistant/core/issues/159800.
"""

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
    DPCodePercentageWrapper,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_default_definitions_without_quirk() -> None:
    """Without quirk, zah67ekd uses DPCodeInvertedPercentageWrapper by default."""
    device = create_device("cl_zah67ekd.json")
    definitions = get_cover_default_definitions(device)
    assert len(definitions) == 1
    definition = definitions["control"]
    assert isinstance(definition.current_position_wrapper, DPCodeInvertedPercentageWrapper)


def test_quirk_sets_non_inverted_flag(filled_quirks_registry: QuirksRegistry) -> None:
    """The quirk sets quirk_cover_position_inverted=False on the device."""
    device = create_device("cl_zah67ekd.json")
    filled_quirks_registry.initialise_device_quirk(device)
    assert getattr(device, "quirk_cover_position_inverted") is False


def test_default_definitions_with_quirk(filled_quirks_registry: QuirksRegistry) -> None:
    """With quirk applied, zah67ekd uses DPCodePercentageWrapper.

    This device reports 0=closed, 100=open (standard HA convention) so
    position must not be inverted.

    See https://github.com/home-assistant/core/issues/159800.
    """
    device = create_device("cl_zah67ekd.json")
    filled_quirks_registry.initialise_device_quirk(device)
    definitions = get_cover_default_definitions(device)
    assert len(definitions) == 1
    definition = definitions["control"]
    assert isinstance(definition.current_position_wrapper, DPCodePercentageWrapper)
    assert not isinstance(definition.current_position_wrapper, DPCodeInvertedPercentageWrapper)
    assert isinstance(definition.set_position_wrapper, DPCodePercentageWrapper)
    assert not isinstance(definition.set_position_wrapper, DPCodeInvertedPercentageWrapper)
