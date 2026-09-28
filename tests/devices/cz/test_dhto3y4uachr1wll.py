"""Test device-level quirk initialisation."""

import json

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry

_CHANNEL_DPCODES = (
    "device_state{n}",
    "cur_power{n}",
    "cur_current{n}",
    "cur_voltage{n}",
    "total_energy{n}",
    "today_acc_energy{n}",
    "warn_power{n}",
)

_CHANNEL_1_DPIDS = (103, 105, 106, 107, 108, 109, 111)
_CHANNEL_2_DPIDS = (113, 115, 116, 117, 118, 119, 121)
_ALL_ENERGY_DPID = 123


def test_quirk_supplies_the_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Tuya advertises nothing, so the quirk supplies the datapoints."""
    device = create_device("cz_dhto3y4uachr1wll.json")

    assert device.status_range == {}
    assert device.function == {}
    assert device.local_strategy == {}

    filled_quirks_registry.initialise_device_quirk(device)

    for channel in (1, 2):
        for dpcode in _CHANNEL_DPCODES:
            assert dpcode.format(n=channel) in device.status_range

    assert "all_energy" in device.status_range

    # Only the two power warning thresholds are writable, so they are the
    # only entries in `function`.
    assert set(device.function) == {"warn_power1", "warn_power2"}


def test_local_strategy_maps_dpids(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The device is local, so dpId reports must resolve to a status code."""
    device = create_device("cz_dhto3y4uachr1wll.json")
    filled_quirks_registry.initialise_device_quirk(device)

    # Without these entries the sharing SDK discards every dpId report.
    assert device.local_strategy[105]["status_code"] == "cur_power1"
    assert device.local_strategy[115]["status_code"] == "cur_power2"
    assert device.local_strategy[123]["status_code"] == "all_energy"
    assert sorted(device.local_strategy) == [
        *_CHANNEL_1_DPIDS,
        *_CHANNEL_2_DPIDS,
        _ALL_ENERGY_DPID,
    ]


def test_electricity_scaling(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Both channels report deci-volt, milli-amp and deci-watt."""
    device = create_device("cz_dhto3y4uachr1wll.json")
    filled_quirks_registry.initialise_device_quirk(device)

    for channel in (1, 2):
        voltage = json.loads(
            device.status_range[f"cur_voltage{channel}"].values
        )
        assert voltage["unit"] == "V"
        assert voltage["scale"] == 1

        current = json.loads(
            device.status_range[f"cur_current{channel}"].values
        )
        assert current["unit"] == "A"
        assert current["scale"] == 3

        power = json.loads(device.status_range[f"cur_power{channel}"].values)
        assert power["unit"] == "W"
        assert power["scale"] == 1

        total = json.loads(device.status_range[f"total_energy{channel}"].values)
        assert total["unit"] == "kWh"
        assert total["scale"] == 3


def test_energy_totals_are_cumulative(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The energy counters are running totals, not per-report increments."""
    device = create_device("cz_dhto3y4uachr1wll.json")
    filled_quirks_registry.initialise_device_quirk(device)

    for dpcode in ("total_energy1", "total_energy2", "all_energy"):
        assert device.status_range[dpcode].report_type is None


def test_device_state_enum_ranges_differ_per_channel(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Channel 1 reports `close` where channel 2 reports `idle`."""
    device = create_device("cz_dhto3y4uachr1wll.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert json.loads(device.status_range["device_state1"].values)["range"] == [
        "close",
        "monitor",
        "working",
        "warning",
    ]
    assert json.loads(device.status_range["device_state2"].values)["range"] == [
        "idle",
        "monitor",
        "working",
        "warning",
    ]
