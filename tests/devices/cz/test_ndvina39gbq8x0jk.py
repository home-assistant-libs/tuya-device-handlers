"""Test the Konyks Priska Max 3 FR light mode enum quirk."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_light_mode_enum_extended(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test that the quirk adds the missing `on` light mode value."""
    device = create_device("cz_ndvina39gbq8x0jk.json")

    before = json.loads(device.status_range["light_mode"].values)["range"]
    assert "on" not in before

    filled_quirks_registry.initialise_device_quirk(device)

    after = json.loads(device.status_range["light_mode"].values)["range"]
    assert "on" in after
