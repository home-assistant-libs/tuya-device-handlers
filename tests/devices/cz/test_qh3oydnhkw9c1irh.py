"""Test device-level quirk initialisation for CZ devices."""

import pytest

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides_power_and_voltage_scaling(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Metered electrical outlet reports power and voltage in deci-units."""
    device = create_device("cz_qh3oydnhkw9c1irh.json")

    definitions = get_sensor_default_definitions(device)
    assert (
        definitions["cur_power"].sensor_wrapper.read_device_status(device)
        == 4681
    )
    assert (
        definitions["cur_voltage"].sensor_wrapper.read_device_status(device)
        == 1156
    )

    filled_quirks_registry.initialise_device_quirk(device)
    definitions = get_sensor_default_definitions(device)

    power_wrapper = definitions["cur_power"].sensor_wrapper
    assert power_wrapper.native_unit == "W"
    assert power_wrapper.read_device_status(device) == pytest.approx(468.1)

    voltage_wrapper = definitions["cur_voltage"].sensor_wrapper
    assert voltage_wrapper.native_unit == "V"
    assert voltage_wrapper.read_device_status(device) == pytest.approx(115.6)

    current_wrapper = definitions["cur_current"].sensor_wrapper
    assert current_wrapper.native_unit == "mA"
    assert current_wrapper.read_device_status(device) == 4178
