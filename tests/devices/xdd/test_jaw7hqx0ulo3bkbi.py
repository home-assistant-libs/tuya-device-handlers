"""Tests for Smart fan (jaw7hqx0ulo3bkbi) quirk."""

from unittest.mock import patch

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_adds_fan_and_light_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Verify missing fan and light datapoints without and with the quirk."""
    device = create_device("xdd_jaw7hqx0ulo3bkbi.json")
    added_dpcodes = (
        "fan_switch",
        "fan_mode",
        "fan_speed",
        "fan_direction",
        "fan_countdown_left",
        "cct",
        "bright_value2",
    )

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        for dpcode in added_dpcodes:
            assert dpcode not in device.status_range
            assert dpcode not in device.function

    filled_quirks_registry.initialise_device_quirk(device)

    for dpcode in added_dpcodes:
        assert dpcode in device.status_range
        assert dpcode in device.function

    assert device.status_range["fan_mode"].values == (
        '{"range": ["fresh", "nature"]}'
    )
    assert device.status_range["fan_speed"].values == (
        '{"unit": "", "min": 1, "max": 6, "scale": 0, "step": 1}'
    )
    assert device.status_range["fan_direction"].values == (
        '{"range": ["forward", "reverse"]}'
    )
    assert device.status_range["fan_countdown_left"].values == (
        '{"unit": "min", "min": 0, "max": 540, "scale": 0, "step": 1}'
    )
    assert device.status_range["cct"].values == (
        '{"range": ["warm", "Neutral", "white"]}'
    )
    assert device.status_range["bright_value2"].values == (
        '{"unit": "%", "min": 1, "max": 100, "scale": 0, "step": 1}'
    )
