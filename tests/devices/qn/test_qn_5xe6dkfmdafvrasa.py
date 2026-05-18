"""Tests for the Quark/Madimack pool heat pump quirk."""

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_quark_pool_heat_pump_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk populates the empty cloud schema with all 25 datapoints."""
    device = create_device("qn_5xe6dkfmdafvrasa.json")

    assert device.function == {}
    assert device.status_range == {}

    filled_quirks_registry.initialise_device_quirk(device)

    # All read-only DPs land in status_range.
    read_dpcodes = {
        "switch1",
        "mode1",
        "child_lock1",
        "temp_set1",
        "work_mode",
        "temp_unit_convert1",
        "fault1",
        "temp_current1",
        "compressor_strength",
        "temp_top",
        "temp_bottom",
        "temp_coiler",
        "temp_venting",
        "temp_effluent",
        "temp_around",
        "fault2",
        "temp_inflow",
        "temp_return",
        "temp_coiler_inside",
        "temp_radiator",
        "expansion_valve",
        "power_w",
        "cool_enable",
        "oc_mode",
        "power",
    }
    assert read_dpcodes.issubset(device.status_range.keys())

    # Settable DPs also land in function.
    write_dpcodes = {
        "switch1",
        "mode1",
        "child_lock1",
        "temp_set1",
        "work_mode",
        "temp_unit_convert1",
        "temp_top",
        "temp_bottom",
        "cool_enable",
    }
    assert write_dpcodes.issubset(device.function.keys())


def test_quark_pool_heat_pump_temperature_scaling(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Inflow/effluent water temps are reported x10; others are whole deg."""
    device = create_device("qn_5xe6dkfmdafvrasa.json")
    filled_quirks_registry.initialise_device_quirk(device)

    # x10 scaled water temperatures.
    assert '"scale": 1' in device.status_range["temp_inflow"].values
    assert '"scale": 1' in device.status_range["temp_effluent"].values

    # Whole-degree refrigerant temperatures.
    assert '"scale": 0' in device.status_range["temp_venting"].values
    assert '"scale": 0' in device.status_range["temp_around"].values
    assert '"scale": 0' in device.status_range["temp_radiator"].values


def test_quark_pool_heat_pump_mode_enum(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The mode datapoint enumerates heating, cooling and auto."""
    device = create_device("qn_5xe6dkfmdafvrasa.json")
    filled_quirks_registry.initialise_device_quirk(device)

    mode = device.function["mode1"]
    assert '"heating"' in mode.values
    assert '"cooling"' in mode.values
    assert '"auto"' in mode.values
