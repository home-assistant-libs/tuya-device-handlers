"""Test the July window air conditioner quirk."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_heat_mode_removed(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk removes the unsupported heat mode from the mode enum."""
    device = create_device("kt_KkdQFqwukvqeoKMa.json")
    original = ["auto", "cold", "hot", "wet", "wind"]
    assert json.loads(device.function["mode"].values)["range"] == original
    assert json.loads(device.status_range["mode"].values)["range"] == original

    filled_quirks_registry.initialise_device_quirk(device)

    expected = ["auto", "cold", "wet", "wind"]
    assert json.loads(device.function["mode"].values)["range"] == expected
    assert json.loads(device.status_range["mode"].values)["range"] == expected
    # Other datapoints are untouched
    assert set(device.function) == {"windspeed", "mode", "temp_set", "switch"}
