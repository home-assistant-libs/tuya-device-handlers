"""Test device-level quirk initialisation."""

import pytest
from tuya_sharing import Manager

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk adds the portal-sourced datapoints absent from the cloud."""
    device = create_device("tdq_jc1afi7ow32okd0h.json")

    assert device.status_range == {}
    assert device.function == {}

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.category == "wsdcg"
    assert set(device.status_range) == {
        "temp_current",
        "humidity_value",
        "battery_state",
        "ext_temp",
    }
    assert device.function == {}


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The added read datapoints surface as sensor definitions."""
    device = create_device("tdq_jc1afi7ow32okd0h.json")

    assert get_sensor_default_definitions(device) == {}

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert set(definitions) == {
        "temp_current",
        "humidity_value",
        "battery_state",
        "ext_temp",
    }


@pytest.mark.parametrize(
    ("raw_value", "expected_temperature"),
    [(-355, -35.5), (122, 12.2), (850, 85.0)],
)
def test_external_probe_mqtt(
    filled_quirks_registry: QuirksRegistry,
    mock_manager: Manager,
    raw_value: int,
    expected_temperature: float,
) -> None:
    """Reports of the external probe are read across its whole range."""
    device = create_device("tdq_jc1afi7ow32okd0h.json")
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    mock_manager._on_device_report(
        device.id,
        [{"dpId": 106, "t": 1757721600000, "value": raw_value}],
    )

    assert device.status["ext_temp"] == raw_value
    wrapper = get_sensor_default_definitions(device)["ext_temp"].sensor_wrapper
    assert wrapper.read_device_status(device) == expected_temperature
