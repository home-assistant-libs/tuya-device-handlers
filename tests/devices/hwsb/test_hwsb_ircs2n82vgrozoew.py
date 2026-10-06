"""Test device-level quirk initialisation for InverFlow pool pump."""

import json

from tuya_sharing import Manager

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_inverflow_pool_pump_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test that quirk adds missing control and telemetry datapoints."""
    device = create_device("hwsb_ircs2n82vgrozoew.json")

    assert device.category == "hwsb"
    assert device.product_id == "ircs2n82vgrozoew"
    assert "switch" not in device.function
    assert "mode" not in device.function
    assert "speed_set" not in device.function
    assert "speed_current" not in device.status_range
    assert "flow_rate" not in device.status_range
    assert "add_ele" not in device.status_range
    assert 105 not in device.local_strategy

    filled_quirks_registry.initialise_device_quirk(device)

    # Function (control DPs)
    assert "switch" in device.function
    assert device.function["switch"].type == "Boolean"

    assert "mode" in device.function
    assert json.loads(device.function["mode"].values)["range"] == [
        "MI",
        "AI",
        "backwash",
    ]

    assert "speed_set" in device.function
    assert json.loads(device.function["speed_set"].values) == {
        "unit": "%",
        "min": 30,
        "max": 120,
        "scale": 0,
        "step": 5,
    }

    # Status range (telemetry DPs)
    assert "speed_current" in device.status_range
    assert json.loads(device.status_range["speed_current"].values) == {
        "unit": "%",
        "min": 0,
        "max": 120,
        "scale": 0,
        "step": 1,
    }

    assert "flow_rate" in device.status_range
    assert json.loads(device.status_range["flow_rate"].values) == {
        "unit": "gal/min",
        "min": 0,
        "max": 1000,
        "scale": 0,
        "step": 1,
    }

    assert "add_ele" in device.status_range
    assert json.loads(device.status_range["add_ele"].values) == {
        "unit": "kWh",
        "min": 0,
        "max": 999999,
        "scale": 2,
        "step": 1,
    }

    # Local strategy for local Tuya protocol control
    assert device.local_strategy[105]["status_code"] == "switch"
    assert device.local_strategy[103]["status_code"] == "mode"
    assert device.local_strategy[111]["status_code"] == "speed_set"
    assert device.local_strategy[102]["status_code"] == "speed_current"
    assert device.local_strategy[112]["status_code"] == "flow_rate"
    assert device.local_strategy[109]["status_code"] == "add_ele"

    # Status preserved from cloud diagnostics
    assert device.status["cur_power"] == 507


def test_inverflow_pool_pump_local_strategy(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check local strategy report handling for pool pump datapoints."""
    device = create_device("hwsb_ircs2n82vgrozoew.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    # Initial status from captured cloud diagnostics
    assert device.status["cur_power"] == 507

    # Verify local protocol 3.3 device interrogation report updates status
    # via local_strategy
    mock_manager._on_device_report(
        device.id,
        [
            {"dpId": 105, "value": True},
            {"dpId": 103, "value": "MI"},
            {"dpId": 111, "value": 80},
            {"dpId": 102, "value": 80},
            {"dpId": 112, "value": 37},
            {"dpId": 109, "value": 50},
        ],
    )
    assert device.status["switch"] is True
    assert device.status["mode"] == "MI"
    assert device.status["speed_set"] == 80
    assert device.status["speed_current"] == 80
    assert device.status["flow_rate"] == 37
    assert device.status["add_ele"] == 50

    # Verify pump stop report
    mock_manager._on_device_report(
        device.id,
        [
            {"dpId": 105, "value": False},
            {"dpId": 102, "value": 0},
        ],
    )
    assert device.status["switch"] is False
    assert device.status["speed_current"] == 0
