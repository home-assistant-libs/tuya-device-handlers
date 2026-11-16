"""Test device-level quirk initialisation for BH devices."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_kettle_expands_temp_setting_quick_c_range(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test dft4ebatvon3ha5s expands temp_setting_quick_c enum range."""
    device = create_device("bh_dft4ebatvon3ha5s.json")

    assert json.loads(device.status_range["temp_setting_quick_c"].values) == {
        "range": ["85", "90"]
    }
    assert json.loads(device.function["temp_setting_quick_c"].values) == {
        "range": ["85", "90"]
    }

    filled_quirks_registry.initialise_device_quirk(device)

    expected = {"range": ["80", "85", "90", "95", "100"]}
    assert (
        json.loads(device.status_range["temp_setting_quick_c"].values)
        == expected
    )
    assert (
        json.loads(device.function["temp_setting_quick_c"].values) == expected
    )
    assert (
        json.loads(device.local_strategy[4]["config_item"]["valueDesc"])
        == expected
    )
