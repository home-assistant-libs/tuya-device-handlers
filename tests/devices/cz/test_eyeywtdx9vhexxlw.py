"""Test device-level quirk initialisation for CZ devices."""

import json

import pytest

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides_power_and_voltage_scaling(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Smart Socket reports power and voltage in deci-units."""
    device = create_device("cz_eyeywtdx9vhexxlw.json")

    definitions = get_sensor_default_definitions(device)
    assert (
        definitions["cur_power"].sensor_wrapper.read_device_status(device)
        == 882
    )
    assert (
        definitions["cur_voltage"].sensor_wrapper.read_device_status(device)
        == 2351
    )

    filled_quirks_registry.initialise_device_quirk(device)
    definitions = get_sensor_default_definitions(device)

    power_wrapper = definitions["cur_power"].sensor_wrapper
    assert power_wrapper.native_unit == "W"
    assert power_wrapper.read_device_status(device) == 88.2

    voltage_wrapper = definitions["cur_voltage"].sensor_wrapper
    assert voltage_wrapper.native_unit == "V"
    assert voltage_wrapper.read_device_status(device) == pytest.approx(235.1)
    assert json.loads(device.status_range["cur_voltage"].values)["max"] == 3000

    current_wrapper = definitions["cur_current"].sensor_wrapper
    assert current_wrapper.native_unit == "mA"
    assert current_wrapper.read_device_status(device) == 375
