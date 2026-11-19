"""Tests for the ceiling fan speed quirk (product_id g0ewlb1vmwqljzji)."""

from unittest.mock import patch

import pytest
from tuya_sharing import CustomerDevice, Manager

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.definition.fan import get_default_definition
from tuya_device_handlers.device_wrapper.fan import FanSpeedEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry


def _speed_wrapper(device: CustomerDevice) -> FanSpeedEnumWrapper:
    """Return the fan speed wrapper for the device."""
    definition = get_default_definition(device)
    assert definition is not None
    wrapper = definition.speed_wrapper
    assert isinstance(wrapper, FanSpeedEnumWrapper)
    return wrapper


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        pytest.param(1, 16, id="speed-1"),
        pytest.param(2, 33, id="speed-2"),
        pytest.param(4, 66, id="speed-4"),
        pytest.param(6, 100, id="speed-6"),
    ],
)
def test_cached_status(
    filled_quirks_registry: QuirksRegistry,
    raw_value: int,
    expected: int,
) -> None:
    """Convert the cached integer speed to the declared string range."""
    device = create_device("fs_g0ewlb1vmwqljzji.json")
    device.status["fan_speed"] = raw_value

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        assert _speed_wrapper(device).read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)
    assert _speed_wrapper(device).read_device_status(device) == expected


def test_local_strategy(filled_quirks_registry: QuirksRegistry) -> None:
    """Map the raw integer speeds to the declared string range."""
    device = create_device("fs_g0ewlb1vmwqljzji.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert device.local_strategy[3]["config_item"]["enumMappingMap"] == {
        "1": {"value": "1"},
        "2": {"value": "2"},
        "3": {"value": "3"},
        "4": {"value": "4"},
        "5": {"value": "5"},
        "6": {"value": "6"},
    }


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        pytest.param(1, "1", id="speed-1"),
        pytest.param(4, "4", id="speed-4"),
        pytest.param(6, "6", id="speed-6"),
    ],
)
def test_mqtt_status(
    filled_quirks_registry: QuirksRegistry,
    mock_manager: Manager,
    raw_value: int,
    expected: str,
) -> None:
    """Keep the speed reported over MQTT instead of discarding it."""
    device = create_device("fs_g0ewlb1vmwqljzji.json")
    filled_quirks_registry.initialise_device_quirk(device)
    mock_manager.device_map[device.id] = device

    mock_manager._on_device_report(
        device.id,
        [{"dpId": 3, "t": 1752456620499, "value": raw_value}],
    )
    assert device.status["fan_speed"] == expected


@pytest.mark.parametrize(
    ("percentage", "expected"),
    [
        pytest.param(16, "1", id="speed-1"),
        pytest.param(33, "2", id="speed-2"),
        pytest.param(66, "4", id="speed-4"),
        pytest.param(100, "6", id="speed-6"),
    ],
)
def test_update_commands(
    filled_quirks_registry: QuirksRegistry, percentage: int, expected: str
) -> None:
    """Keep sending the speed as the declared string value."""
    device = create_device("fs_g0ewlb1vmwqljzji.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert _speed_wrapper(device).get_update_commands(device, percentage) == [
        {"code": "fan_speed", "value": expected}
    ]
