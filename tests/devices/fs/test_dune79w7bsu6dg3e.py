"""Tests for the Duux Whisper Flex oscillation quirk."""

from unittest.mock import patch

import pytest
from tuya_sharing import CustomerDevice, Manager

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper
from tuya_device_handlers.registry import QuirksRegistry


def _get_wrapper(device: CustomerDevice, dpcode: str) -> DPCodeBooleanWrapper:
    """Return a boolean wrapper for an oscillation datapoint."""
    wrapper = DPCodeBooleanWrapper.find_dpcode(
        device, dpcode, prefer_function=True
    )
    assert wrapper is not None
    return wrapper


@pytest.mark.parametrize(
    ("dpcode", "raw_value", "expected"),
    [
        pytest.param("switch_horizontal", "false", False, id="horizontal-off"),
        pytest.param("switch_horizontal", "true", True, id="horizontal-on"),
        pytest.param("switch_vertical", "false", False, id="vertical-off"),
        pytest.param("switch_vertical", "true", True, id="vertical-on"),
    ],
)
def test_cached_status(
    filled_quirks_registry: QuirksRegistry,
    dpcode: str,
    raw_value: str,
    expected: bool,
) -> None:
    """Convert cached lowercase boolean strings."""
    device = create_device("fs_dune79w7bsu6dg3e.json")
    device.status[dpcode] = raw_value

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        assert _get_wrapper(device, dpcode).read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)
    assert _get_wrapper(device, dpcode).read_device_status(device) is expected


def test_local_strategy(filled_quirks_registry: QuirksRegistry) -> None:
    """Replace string mappings with native booleans."""
    device = create_device("fs_dune79w7bsu6dg3e.json")
    filled_quirks_registry.initialise_device_quirk(device)

    expected_mapping = {
        "0": {"value": False},
        "1": {"value": True},
    }
    assert device.local_strategy[4]["config_item"]["enumMappingMap"] == (
        expected_mapping
    )
    assert device.local_strategy[5]["config_item"]["enumMappingMap"] == (
        expected_mapping
    )


@pytest.mark.parametrize(
    ("dpid", "dpcode", "raw_value", "expected"),
    [
        pytest.param(4, "switch_horizontal", 0, False, id="horizontal-off"),
        pytest.param(4, "switch_horizontal", 1, True, id="horizontal-on"),
        pytest.param(5, "switch_vertical", 0, False, id="vertical-off"),
        pytest.param(5, "switch_vertical", 1, True, id="vertical-on"),
    ],
)
def test_mqtt_status(
    filled_quirks_registry: QuirksRegistry,
    mock_manager: Manager,
    dpid: int,
    dpcode: str,
    raw_value: int,
    expected: bool,
) -> None:
    """Map raw MQTT values to native booleans."""
    device = create_device("fs_dune79w7bsu6dg3e.json")
    filled_quirks_registry.initialise_device_quirk(device)
    mock_manager.device_map[device.id] = device

    mock_manager._on_device_report(
        device.id,
        [{"dpId": dpid, "t": 1752456620499, "value": raw_value}],
    )
    assert device.status[dpcode] is expected


@pytest.mark.parametrize(
    ("dpcode", "value"),
    [
        pytest.param("switch_horizontal", False, id="horizontal-off"),
        pytest.param("switch_horizontal", True, id="horizontal-on"),
        pytest.param("switch_vertical", False, id="vertical-off"),
        pytest.param("switch_vertical", True, id="vertical-on"),
    ],
)
def test_update_commands(
    filled_quirks_registry: QuirksRegistry, dpcode: str, value: bool
) -> None:
    """Send native boolean commands for both oscillation axes."""
    device = create_device("fs_dune79w7bsu6dg3e.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert _get_wrapper(device, dpcode).get_update_commands(device, value) == [
        {"code": dpcode, "value": value}
    ]
