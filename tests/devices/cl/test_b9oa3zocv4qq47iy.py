"""Test device-level quirk initialisation."""

from tests import create_device
from tests.devices.cover_helpers import get_cover_default_definitions
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_suppresses_percent_state(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """A-OK AM45 Plus advertises ``percent_state`` but never pushes updates.

    The quirk must drop the DP so the default CL mapping falls back to
    ``percent_control``. See
    https://github.com/home-assistant/core/issues/168493.
    """
    device = create_device("cl_b9oa3zocv4qq47iy.json")

    assert "percent_state" in device.status_range
    assert "percent_state" in device.status
    assert 3 in device.local_strategy

    filled_quirks_registry.initialise_device_quirk(device)

    assert "percent_state" not in device.status_range
    assert "percent_state" not in device.status
    assert 3 not in device.local_strategy


def test_cover_definition(filled_quirks_registry: QuirksRegistry) -> None:
    """A-OK AM45 Plus advertises ``percent_state`` but never pushes updates.

    The quirk must drop the DP so the default CL mapping falls back to
    ``percent_control``. See
    https://github.com/home-assistant/core/issues/168493.
    """
    device = create_device("cl_b9oa3zocv4qq47iy.json")

    # Default without quirk would be DPCodeInvertedPercentageWrapper
    # with dpcode "percent_state"
    definitions = get_cover_default_definitions(device)
    assert len(definitions) == 1
    definition = definitions[0]
    assert isinstance(
        definition.current_position_wrapper, DPCodeInvertedPercentageWrapper
    )
    assert definition.current_position_wrapper.dpcode == "percent_state"

    filled_quirks_registry.initialise_device_quirk(device)

    # With quirk applied it is still DPCodeInvertedPercentageWrapper
    # but with dpcode "percent_control"
    definitions = get_cover_default_definitions(device)
    assert len(definitions) == 1
    definition = definitions[0]
    assert isinstance(
        definition.current_position_wrapper, DPCodeInvertedPercentageWrapper
    )
    assert definition.current_position_wrapper.dpcode == "percent_control"
