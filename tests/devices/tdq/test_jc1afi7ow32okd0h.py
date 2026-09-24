"""Test device-level quirk initialisation."""

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
