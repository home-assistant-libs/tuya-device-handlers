"""Tests for the Absina Mobile Wallbox 11 kW (tj9l3ghsjnbdjom6) quirk.

The charger reports its status and measurements on vendor-specific DPs that
are missing from the cloud spec, while the standard DPs it advertises are
never reported or have no effect.
"""

import json

import pytest
from tuya_sharing import CustomerDevice

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry
from tuya_device_handlers.type_information import (
    EnumTypeInformation,
    IntegerTypeInformation,
)

_FIXTURE = "qccdz_tj9l3ghsjnbdjom6.json"

# Vendor DP id -> standard DP code the quirk maps it to.
_MAPPED_DPIDS = {
    101: "work_state",
    102: "cur_voltage",
    105: "cur_current",
    109: "power_total",
    110: "temp_current",
    112: "charge_energy_once",
    121: "charge_time",
}

# Standard DPs that are never reported, have no effect, or are rejected as
# cloud commands. DP 3 and DP 25 are replaced by DP 101 and DP 112.
_REMOVED_DPIDS = {
    3: "work_state",
    14: "work_mode",
    15: "balance_energy",
    16: "clear_energy",
    18: "switch",
    25: "charge_energy_once",
}

_WORK_STATES = [
    "no_connet",
    "connect",
    "charing",
    "wait_rfid",
    "finish",
    "wait_charing",
    "error",
]


def _create_quirked_device(registry: QuirksRegistry) -> CustomerDevice:
    device = create_device(_FIXTURE)
    registry.initialise_device_quirk(device)
    return device


def test_quirk_adds_measurements(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Without the quirk the charger exposes no measurements."""
    device = create_device(_FIXTURE)

    for dpcode in ("cur_voltage", "cur_current", "power_total", "charge_time"):
        assert dpcode not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    for dpcode in _MAPPED_DPIDS.values():
        assert dpcode in device.status_range


def test_local_strategy_maps_dpids(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """DP id reports must resolve to the standard codes."""
    device = _create_quirked_device(filled_quirks_registry)

    for dpid, dpcode in _MAPPED_DPIDS.items():
        assert device.local_strategy[dpid]["status_code"] == dpcode


def test_quirk_removes_unused_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Dead or uncontrollable standard DPs are removed."""
    device = create_device(_FIXTURE)
    assert set(device.function) == {"work_mode", "clear_energy", "switch"}
    assert set(_REMOVED_DPIDS) <= set(device.local_strategy)

    filled_quirks_registry.initialise_device_quirk(device)

    for dpid in _REMOVED_DPIDS:
        assert dpid not in device.local_strategy
    for dpcode in ("work_mode", "balance_energy", "clear_energy", "switch"):
        assert dpcode not in device.status_range
        assert dpcode not in device.function
    # The charger has nothing that can be controlled through the cloud.
    assert device.function == {}


def test_work_state_uses_vendor_values(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """DP 101 replaces DP 3, with the device's own (misspelled) values."""
    device = create_device(_FIXTURE)
    type_information = EnumTypeInformation.find_dpcode(device, "work_state")
    assert type_information is not None
    assert "charger_free" in type_information.range

    filled_quirks_registry.initialise_device_quirk(device)
    device.status["work_state"] = "wait_charing"

    type_information = EnumTypeInformation.find_dpcode(device, "work_state")
    assert type_information is not None
    assert type_information.range == _WORK_STATES
    assert type_information.read_device_value(device) == "wait_charing"


@pytest.mark.parametrize(
    ("dpcode", "unit", "raw_value", "expected"),
    [
        ("cur_voltage", "V", 415, 415),
        ("cur_current", "A", 153, 15.3),
        ("power_total", "kW", 109, 10.9),
        ("temp_current", "°C", 356, 35.6),
        ("charge_energy_once", "kWh", 79, 7.9),
        ("charge_time", "h", 8, 0.8),
    ],
)
def test_measurement_scaling(
    filled_quirks_registry: QuirksRegistry,
    dpcode: str,
    unit: str,
    raw_value: int,
    expected: float,
) -> None:
    """Values match the vendor app (e.g. raw 109 is 10.9 kW)."""
    device = _create_quirked_device(filled_quirks_registry)
    device.status[dpcode] = raw_value

    type_information = IntegerTypeInformation.find_dpcode(device, dpcode)
    assert type_information is not None
    assert type_information.unit == unit
    assert type_information.read_device_value(device) == pytest.approx(expected)


def test_session_energy_comes_from_vendor_dp(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """charge_energy_once is redefined with DP 112's range and scale."""
    device = create_device(_FIXTURE)
    values = json.loads(device.status_range["charge_energy_once"].values)
    assert values["scale"] == 2

    filled_quirks_registry.initialise_device_quirk(device)

    values = json.loads(device.status_range["charge_energy_once"].values)
    assert values["scale"] == 1
    assert values["min"] == 0
    assert values["max"] == 10000
