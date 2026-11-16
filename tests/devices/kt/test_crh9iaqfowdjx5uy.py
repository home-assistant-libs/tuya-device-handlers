"""Test the Kogan portable AC quirk."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_portable_ac_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test the quirk corrects the temperature and HVAC mode schemas."""
    device = create_device("kt_crh9iaqFowdJX5UY.json")

    assert "temp_current" not in device.status_range
    assert json.loads(device.function["temp_set"].values) == {
        "min": 0,
        "unit": "℃",
        "scale": 0,
        "max": 50,
        "step": 1,
    }
    assert json.loads(device.function["mode"].values)["range"] == [
        "auto",
        "cold",
        "hot",
        "wet",
        "wind",
        "eco",
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    expected_temperature_range = {
        "unit": "℃",
        "min": 16,
        "max": 30,
        "scale": 0,
        "step": 1,
    }
    assert json.loads(device.function["temp_set"].values) == (
        expected_temperature_range
    )
    assert json.loads(device.status_range["temp_set"].values) == (
        expected_temperature_range
    )
    assert json.loads(device.status_range["temp_current"].values) == {
        "unit": "℃",
        "min": -7,
        "max": 98,
        "scale": 0,
        "step": 1,
    }
    assert json.loads(device.function["mode"].values)["range"] == [
        "cold",
        "hot",
        "wet",
        "wind",
    ]
    assert json.loads(device.status_range["mode"].values)["range"] == [
        "cold",
        "hot",
        "wet",
        "wind",
    ]
