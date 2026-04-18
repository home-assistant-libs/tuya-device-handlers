"""Test device-level quirk initialisation."""

from __future__ import annotations

from tuya_device_handlers.registry import QuirksRegistry

from . import create_device


def test_am45_plus_suppresses_percent_state(
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
