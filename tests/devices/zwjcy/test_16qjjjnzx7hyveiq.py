"""Test Solar Soil Sensor moisture recovery."""

import json

import pytest
from tuya_sharing import Manager

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(filled_quirks_registry: QuirksRegistry) -> None:
    """Solar Soil Sensor adds read-only moisture without changing other DPs."""
    device = create_device("zwjcy_16qjjjnzx7hyveiq.json")
    original_status = device.status.copy()
    original_strategy = device.local_strategy.copy()
    original_function = device.function.copy()
    original_ranges = device.status_range.copy()
    assert 111 not in device.local_strategy
    assert "humidity" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.status == original_status
    assert device.function == original_function
    for dpid, strategy in original_strategy.items():
        assert device.local_strategy[dpid] == strategy
    for code, definition in original_ranges.items():
        assert device.status_range[code] == definition
    assert device.local_strategy[111]["status_code"] == "humidity"
    assert json.loads(device.status_range["humidity"].values) == {
        "unit": "%",
        "min": 0,
        "max": 100,
        "scale": 0,
        "step": 1,
    }


@pytest.mark.parametrize("raw_value", [0, 7, 30, 66, 100])
def test_mqtt_moisture_report(
    filled_quirks_registry: QuirksRegistry,
    mock_manager: Manager,
    raw_value: int,
) -> None:
    """Solar Soil Sensor accepts previously discarded moisture reports."""
    device = create_device("zwjcy_16qjjjnzx7hyveiq.json")
    mock_manager.device_map[device.id] = device
    report = [{"dpId": 111, "value": raw_value, "t": 1789540701486}]
    assert "humidity" not in get_sensor_default_definitions(device)
    mock_manager._on_device_report(device.id, report)
    assert "humidity" not in device.status

    filled_quirks_registry.initialise_device_quirk(device)
    wrapper = get_sensor_default_definitions(device)["humidity"].sensor_wrapper
    assert wrapper.native_unit == "%"
    assert wrapper.read_device_status(device) is None

    mock_manager._on_device_report(device.id, report)
    assert device.status["humidity"] == raw_value
    assert wrapper.read_device_status(device) == raw_value
