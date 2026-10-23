"""Test the L15 Ultra cistern enum quirk."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_cistern_enum_extended(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The quirk adds the missing `closed` cistern value."""
    device = create_device("sd_oaelsi57ejdiavfh.json")

    # Without the quirk, the cloud function list lacks `closed`.
    before = json.loads(device.function["cistern"].values)["range"]
    assert "closed" not in before

    filled_quirks_registry.initialise_device_quirk(device)

    after = json.loads(device.function["cistern"].values)["range"]
    assert "closed" in after
