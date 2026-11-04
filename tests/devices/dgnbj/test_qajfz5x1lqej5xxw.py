"""Test device-level quirk initialisation for the 5 in 1 tester (dgnbj)."""

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The 5 in 1 tester registers the ph_current DP."""
    device = create_device("dgnbj_qajfz5x1lqej5xxw.json")

    assert "temp_current" in device.status_range
    assert "ph_current" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert "temp_current" in device.status_range
    assert "ph_current" in device.status_range


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The 5 in 1 tester exposes the pH sensor after the quirk."""
    device = create_device("dgnbj_qajfz5x1lqej5xxw.json")

    definitions = get_sensor_default_definitions(device)
    assert "temp_current" in definitions
    assert "ph_current" not in definitions

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert "temp_current" in definitions
    assert "ph_current" in definitions
