"""Test the July window air conditioner quirk."""

import json

from tuya_sharing import Manager

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_mode_and_extra_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk removes heat mode and adds the ECO and sleep datapoints."""
    device = create_device("kt_KkdQFqwukvqeoKMa.json")
    original = ["auto", "cold", "hot", "wet", "wind"]
    assert json.loads(device.function["mode"].values)["range"] == original
    assert "mode_eco" not in device.function
    assert "sleep" not in device.function

    filled_quirks_registry.initialise_device_quirk(device)

    expected = ["auto", "cold", "wet", "wind"]
    assert json.loads(device.function["mode"].values)["range"] == expected
    assert json.loads(device.status_range["mode"].values)["range"] == expected
    for dpcode in ("mode_eco", "sleep"):
        assert device.function[dpcode].type == "Boolean"
        assert device.status_range[dpcode].type == "Boolean"


def test_mqtt(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check ECO and sleep reports are mapped from their DP ids."""
    device = create_device("kt_KkdQFqwukvqeoKMa.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    mock_manager._on_device_report(
        device.id,
        [
            {"dpId": 8, "t": 1794100000000, "value": True},
            {"dpId": 101, "t": 1794100000000, "value": False},
        ],
    )
    assert device.status["mode_eco"] is True
    assert device.status["sleep"] is False
