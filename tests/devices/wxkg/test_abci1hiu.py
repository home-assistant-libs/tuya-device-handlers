"""Test the MOES four-button Zigbee scene remote quirk."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_first_button_is_normalised(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Expose button 1 under the same naming scheme as buttons 2-4."""
    device = create_device("wxkg_abci1hiu.json")

    assert "switch1_value" in device.status_range
    assert "switch_mode1" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert "switch_mode1" in device.status_range
    assert json.loads(device.status_range["switch_mode1"].values)["range"] == [
        "click",
        "double_click",
        "press",
    ]
    assert device.local_strategy[1]["status_code"] == "switch_mode1"
    assert device.local_strategy[1]["config_item"]["enumMappingMap"] == {
        "single_click": {"code": "switch_mode1", "value": "click"},
        "double_click": {"code": "switch_mode1", "value": "double_click"},
        "long_press": {"code": "switch_mode1", "value": "press"},
    }
    for button in (2, 3, 4):
        assert f"switch_mode{button}" in device.status_range
