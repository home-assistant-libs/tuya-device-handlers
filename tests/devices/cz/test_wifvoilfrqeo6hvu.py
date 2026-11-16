"""Test device-level quirk initialisation for CZ devices."""

import json

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.device_wrapper.sensor import DeltaIntegerWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Smart Socket rescales the electricity DPs and fixes the energy unit."""
    device = create_device("cz_wifvoilfrqeo6hvu.json")

    # The cloud declares scale=0 for voltage/power, so the values read
    # 10x too high, and reports the energy unit as Chinese for kWh.
    definitions = get_sensor_default_definitions(device)
    assert (
        definitions["cur_voltage"].sensor_wrapper.read_device_status(device)
        == 2306
    )
    assert (
        definitions["cur_power"].sensor_wrapper.read_device_status(device)
        == 2941
    )
    assert definitions["add_ele"].sensor_wrapper.native_unit == "\u5ea6"

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)

    # Voltage/power are reported in deci-volt/deci-watt
    assert json.loads(device.status_range["cur_voltage"].values)["max"] == 5000

    voltage_wrapper = definitions["cur_voltage"].sensor_wrapper
    assert voltage_wrapper.native_unit == "V"
    assert voltage_wrapper.read_device_status(device) == 230.6

    power_wrapper = definitions["cur_power"].sensor_wrapper
    assert power_wrapper.native_unit == "W"
    assert power_wrapper.read_device_status(device) == 294.1

    # Current was already correct and must be untouched
    current_wrapper = definitions["cur_current"].sensor_wrapper
    assert current_wrapper.native_unit == "mA"
    assert current_wrapper.read_device_status(device) == 1275

    # Energy is reported in Wh increments, exposed as kWh
    energy_wrapper = definitions["add_ele"].sensor_wrapper
    assert energy_wrapper.native_unit == "kWh"


def test_energy_keeps_delta_accumulation(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """add_ele keeps report_type=sum, so deltas are accumulated."""
    device = create_device("cz_wifvoilfrqeo6hvu.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert device.status_range["add_ele"].report_type == "sum"

    definitions = get_sensor_default_definitions(device)
    energy_wrapper = definitions["add_ele"].sensor_wrapper
    assert isinstance(energy_wrapper, DeltaIntegerWrapper)

    # Accumulation starts at 0; a raw delta of 10 is scaled to 0.01 kWh
    assert energy_wrapper.read_device_status(device) == 0
    assert not energy_wrapper.skip_update(
        device, ["add_ele"], dp_timestamps={"add_ele": 123456789}
    )
    assert energy_wrapper.read_device_status(device) == 0.01
