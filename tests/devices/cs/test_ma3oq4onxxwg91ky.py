"""Test device-level quirk initialisation for CS devices."""

import json

from tests import create_device
from tests.integration_helpers.binary_sensor import (
    get_binary_sensor_default_definitions,
)
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Eeese Otto extends the fault bitmap with the tankfull label."""
    device = create_device("cs_ma3oq4onxxwg91ky.json")

    assert json.loads(device.status_range["fault"].values) == {
        "label": ["E1", "E2"]
    }

    filled_quirks_registry.initialise_device_quirk(device)

    assert json.loads(device.status_range["fault"].values) == {
        "label": ["E1", "E2", "tankfull"]
    }


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Eeese Otto exposes a tank full binary sensor."""
    device = create_device("cs_ma3oq4onxxwg91ky.json")

    definitions = get_binary_sensor_default_definitions(device)
    assert "tankfull" not in definitions

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_binary_sensor_default_definitions(device)
    assert "tankfull" in definitions
