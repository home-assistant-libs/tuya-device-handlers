"""Test the PC311_W_TY energy meter quirk."""

import json

import pytest

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry

ENERGY = {"unit": "kWh", "min": 0, "max": 999999999, "scale": 2, "step": 1}
CURRENT_CIRCUIT = {
    "unit": "A",
    "min": 0,
    "max": 1000000,
    "scale": 3,
    "step": 1,
}
POWER = {
    "unit": "W",
    "min": -1000000000,
    "max": 1000000000,
    "scale": 0,
    "step": 1,
}
REACTIVE_POWER = {
    "unit": "var",
    "min": -1000000000,
    "max": 1000000000,
    "scale": 0,
    "step": 1,
}
PF = {"unit": "", "min": 0, "max": 100, "scale": 2, "step": 1}

EXPECTED = {
    "total_energy1": ENERGY,
    "reverse_energy1": ENERGY,
    "total_energy2": ENERGY,
    "reverse_energy2": ENERGY,
    "cur_current": {
        "unit": "A",
        "min": 0,
        "max": 1000000000,
        "scale": 3,
        "step": 1,
    },
    "cur_voltage": {
        "unit": "V",
        "min": 0,
        "max": 1000000,
        "scale": 1,
        "step": 1,
    },
    "cur_current1": CURRENT_CIRCUIT,
    "cur_power1": POWER,
    "power_factor1": PF,
    "cur_current2": CURRENT_CIRCUIT,
    "cur_power2": POWER,
    "power_factor2": PF,
    "ct_direction1": {},
    "ct_direction2": {},
    "reactive_power1": REACTIVE_POWER,
    "reactive_power2": REACTIVE_POWER,
    "supply_frequency": {
        "unit": "Hz",
        "min": 0,
        "max": 10000,
        "scale": 0,
        "step": 1,
    },
}


@pytest.mark.parametrize(("dpcode", "expected"), EXPECTED.items())
def test_energy_meter_datapoints_added(
    filled_quirks_registry: QuirksRegistry,
    dpcode: str,
    expected: dict,
) -> None:
    """The quirk adds the missing datapoint with the right definition."""
    device = create_device("zndb_vfwxetkavqrvg02u.json")

    # BEFORE the quirk: the cloud only knows the three total datapoints.
    assert dpcode not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    # AFTER the quirk: the datapoint is present and correctly defined.
    assert json.loads(device.status_range[dpcode].values) == expected


@pytest.mark.parametrize(
    ("dpid", "dpcode"),
    [
        (101, "total_energy1"),
        (102, "reverse_energy1"),
        (103, "total_energy2"),
        (104, "reverse_energy2"),
        (105, "cur_current"),
        (106, "cur_voltage"),
        (107, "cur_current1"),
        (108, "cur_power1"),
        (109, "power_factor1"),
        (110, "cur_current2"),
        (111, "cur_power2"),
        (112, "power_factor2"),
        (113, "ct_direction1"),
        (114, "ct_direction2"),
        (115, "reactive_power1"),
        (116, "reactive_power2"),
        (117, "supply_frequency"),
    ],
)
def test_energy_meter_local_strategy(
    filled_quirks_registry: QuirksRegistry,
    dpid: int,
    dpcode: str,
) -> None:
    """Missing DPID reports resolve to the correct status codes."""
    device = create_device("zndb_vfwxetkavqrvg02u.json")
    assert dpid not in device.local_strategy

    filled_quirks_registry.initialise_device_quirk(device)

    strategy = device.local_strategy[dpid]
    assert strategy["status_code"] == dpcode
    assert json.loads(strategy["config_item"]["statusFormat"]) == {dpcode: "$"}
