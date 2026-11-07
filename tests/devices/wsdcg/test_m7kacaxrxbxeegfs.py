"""Test device-level quirk initialisation for WSDCG devices."""

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Tem&Hum Sensor with Probe registers the temp_current DP."""
    device = create_device("wsdcg_m7kacaxrxbxeegfs.json")

    assert "va_temperature" in device.status_range
    assert "ext_temp" not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    assert "va_temperature" in device.status_range
    assert "ext_temp" in device.status_range


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Tem&Hum Sensor with Probe exposes both temperature sensors."""
    device = create_device("wsdcg_m7kacaxrxbxeegfs.json")

    definitions = get_sensor_default_definitions(device)
    assert "va_temperature" in definitions
    assert "ext_temp" not in definitions

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    assert "va_temperature" in definitions
    assert "ext_temp" in definitions
