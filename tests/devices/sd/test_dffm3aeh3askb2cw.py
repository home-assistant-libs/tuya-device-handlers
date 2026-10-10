"""Test the Abir K30 mode enum quirk."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_mode_enum_extended(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The quirk adds the missing `goto_charge` mode value."""
    device = create_device("sd_dffm3aeh3askb2cw.json")

    # BEFORE the quirk: the cloud only knows `auto`.
    before = json.loads(device.status_range["mode"].values)["range"]
    assert "goto_charge" not in before

    filled_quirks_registry.initialise_device_quirk(device)

    # AFTER the quirk: the full list is present.
    after = json.loads(device.status_range["mode"].values)["range"]
    assert "goto_charge" in after
