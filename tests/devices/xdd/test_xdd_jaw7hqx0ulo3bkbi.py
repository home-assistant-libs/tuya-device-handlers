"""Tests for Smart fan (jaw7hqx0ulo3bkbi) quirk."""

from tuya_device_handlers.registry import QuirksRegistry

from tests import create_device


def test_quirk_registers_fan_and_light_dps(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Verify extended fan and light DPs are registered when quirk is applied."""
    device = create_device("xdd_jaw7hqx0ulo3bkbi.json")
    filled_quirks_registry.initialise_device_quirk(device)

    for dpcode in (
        "switch_led",
        "bright_value",
        "fan_switch",
        "fan_mode",
        "fan_speed",
        "fan_direction",
        "fan_countdown_left",
        "cct",
        "bright_value2",
    ):
        assert dpcode in device.function
        assert dpcode in device.status_range
