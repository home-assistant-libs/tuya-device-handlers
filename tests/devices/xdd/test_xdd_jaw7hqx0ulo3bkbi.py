"""Tests for Smart fan (jaw7hqx0ulo3bkbi) quirk."""

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_adds_fan_and_light_dps(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Verify fan and light datapoints are added for product jaw7hqx0ulo3bkbi."""
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

    assert device.status_range["fan_speed"].values == (
        '{"unit": "", "min": 1, "max": 6, "scale": 0, "step": 1}'
    )
    assert device.status_range["fan_mode"].values == '{"range": ["fresh"]}'
    assert device.status_range["fan_direction"].values == (
        '{"range": ["forward"]}'
    )
    assert device.status_range["cct"].values == '{"range": ["white"]}'
