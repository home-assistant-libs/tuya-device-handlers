"""Test the PC311_W_TY energy meter quirk."""

import json

import pytest

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry

ENERGY = {"unit": "kWh", "min": 0, "max": 999999999, "scale": 2, "step": 1}
CURRENT = {
    "unit": "A",
    "min": -999999999,
    "max": 999999999,
    "scale": 3,
    "step": 1,
}
POWER = {
    "unit": "W",
    "min": -999999999,
    "max": 999999999,
    "scale": 0,
    "step": 1,
}
PF = {"unit": "", "min": 0, "max": 100, "scale": 2, "step": 1}

EXPECTED = {
    "total_energy1": ENERGY,
    "reserve_energy_circuit_1": ENERGY,
    "total_energy2": ENERGY,
    "reserve_energy_circuit_2": ENERGY,
    "cur_current": CURRENT,
    "cur_voltage": {
        "unit": "V",
        "min": 0,
        "max": 999999999,
        "scale": 1,
        "step": 1,
    },
    "cur_current1": CURRENT,
    "cur_power1": POWER,
    "pf_circuit_1": PF,
    "cur_current2": CURRENT,
    "cur_power2": POWER,
    "pf_circuit_2": PF,
    "supply_frequency": {
        "unit": "Hz",
        "min": 0,
        "max": 999,
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
