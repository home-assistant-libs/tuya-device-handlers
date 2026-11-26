"""Tests for m1ggi8iay3aa8g9u humidity and illuminance quirk."""

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_adds_humidity_and_illuminance_dps(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Verify humidity_value and illuminance_value datapoints are added."""
    device = create_device("<category>_m1ggi8iay3aa8g9u.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert "humidity_value" in device.status_range
    assert "illuminance_value" in device.status_range

    assert device.status_range["humidity_value"].values == (
        '{"unit": "%", "min": 0, "max": 100, "scale": 0, "step": 1}'
    )
    assert device.status_range["illuminance_value"].values == (
        '{"unit": "lx", "min": 0, "max": 100000, "scale": 0, "step": 1}'
    )
