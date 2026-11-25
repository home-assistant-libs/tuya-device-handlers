"""Test the MOES four-button Zigbee scene remote quirk."""

import pytest
from tuya_sharing import Manager

from tests import create_device
from tuya_device_handlers.definition.event import get_default_definition
from tuya_device_handlers.registry import QuirksRegistry


def test_button_1_event_definition(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Expose a default event definition for button 1 with the quirk."""
    device = create_device("wxkg_abci1hiu.json")

    assert get_default_definition(device, "switch_mode1") is None

    filled_quirks_registry.initialise_device_quirk(device)

    for button in (1, 2, 3, 4):
        assert (
            get_default_definition(device, f"switch_mode{button}") is not None
        )


@pytest.mark.parametrize("button", [1, 2, 3, 4])
@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("single_click", "click"),
        ("double_click", "double_click"),
        ("long_press", "press"),
    ],
)
def test_mqtt_status(
    filled_quirks_registry: QuirksRegistry,
    mock_manager: Manager,
    button: int,
    raw_value: str,
    expected: str,
) -> None:
    """Convert each raw button report and update only its own status."""
    device = create_device("wxkg_abci1hiu.json")
    filled_quirks_registry.initialise_device_quirk(device)
    mock_manager.device_map[device.id] = device

    dpcode = f"switch_mode{button}"
    device.status.pop(dpcode, None)
    expected_status = {**device.status, dpcode: expected}

    mock_manager._on_device_report(
        device.id,
        [{"dpId": button, "t": 1752456620499, "value": raw_value}],
    )

    assert device.status[dpcode] == expected
    assert device.status == expected_status
