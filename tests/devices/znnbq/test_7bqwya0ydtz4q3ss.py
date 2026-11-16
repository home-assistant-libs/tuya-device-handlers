"""Test device-level quirk initialisation for ZNNBQ devices."""

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides_wvc_micro_inverter_power_unit(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """WVC micro inverter reports power_total as kW instead of W."""
    device = create_device("znnbq_7bqwya0ydtz4q3ss.json")

    definitions = get_sensor_default_definitions(device)
    power_wrapper = definitions["power_total"].sensor_wrapper

    # Before the quirk, the cloud metadata declares kW with scale 3.
    # This gives a native value like 179.641 kW, which Home Assistant later
    # exposes as 179641 W.
    assert power_wrapper.native_unit == "kW"
    assert power_wrapper.read_device_status(device) == 179.641

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    power_wrapper = definitions["power_total"].sensor_wrapper

    # After the quirk, the same scaled native value is correctly expressed in W.
    assert power_wrapper.native_unit == "W"
    assert power_wrapper.read_device_status(device) == 179.641
