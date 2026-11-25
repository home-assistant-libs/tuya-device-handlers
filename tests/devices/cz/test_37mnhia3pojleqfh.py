"""Tests for the 37mnhia3pojleqfh smart plug scaling quirk.

Without the quirk the voltage sensor reads 2255 V and the power sensor
reads 40 W. See the quirk module for the scale evidence.
"""

from unittest.mock import patch

import pytest

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides_voltage_and_power_scaling(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Voltage and power are rescaled from deci-units to V and W."""
    device = create_device("cz_37mnhia3pojleqfh.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_sensor_default_definitions(device)

    voltage_wrapper = definitions["cur_voltage"].sensor_wrapper
    assert voltage_wrapper.native_unit == "V"
    assert voltage_wrapper.read_device_status(device) == 2255

    power_wrapper = definitions["cur_power"].sensor_wrapper
    assert power_wrapper.native_unit == "W"
    assert power_wrapper.read_device_status(device) == 40

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)

    voltage_wrapper = definitions["cur_voltage"].sensor_wrapper
    assert voltage_wrapper.native_unit == "V"
    voltage = voltage_wrapper.read_device_status(device)
    assert voltage == pytest.approx(225.5)

    power_wrapper = definitions["cur_power"].sensor_wrapper
    assert power_wrapper.native_unit == "W"
    power = power_wrapper.read_device_status(device)
    assert power == pytest.approx(4.0)

    # The rescaled voltage and the reported power must agree with Ohm's law
    # for the current the same report carries: 225.5 V x 18 mA = 4.06 W.
    current = definitions["cur_current"].sensor_wrapper.read_device_status(
        device
    )
    assert isinstance(voltage, float)
    assert isinstance(power, float)
    assert current == 18
    assert voltage * current / 1000 == pytest.approx(power, abs=0.1)


def test_quirk_leaves_current_untouched(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Current is already reported in mA with scale=0 and must not change."""
    device = create_device("cz_37mnhia3pojleqfh.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_sensor_default_definitions(device)
    before = definitions["cur_current"].sensor_wrapper.read_device_status(
        device
    )

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    current_wrapper = definitions["cur_current"].sensor_wrapper
    assert current_wrapper.native_unit == "mA"
    assert current_wrapper.read_device_status(device) == before == 18


def test_quirk_keeps_high_mains_voltage_in_range(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The raised maximum keeps voltages above 250.0 V from being dropped."""
    device = create_device("cz_37mnhia3pojleqfh.json")
    filled_quirks_registry.initialise_device_quirk(device)

    # 2524 deci-volts = 252.4 V, above the cloud-declared 2500 maximum.
    device.status["cur_voltage"] = 2524

    definitions = get_sensor_default_definitions(device)
    voltage_wrapper = definitions["cur_voltage"].sensor_wrapper
    assert voltage_wrapper.read_device_status(device) == pytest.approx(252.4)
