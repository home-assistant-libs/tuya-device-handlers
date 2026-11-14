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
    device = create_device("cz_79a7z01v3n35kytb.json")

    assert device.status_range == {}
    assert device.function == {}
    assert device.local_strategy == {}

    filled_quirks_registry.initialise_device_quirk(device)

    assert set(device.status_range) == {
        "all_energy",
        *(
            dpcode.format(n=channel)
            for channel in (1, 2)
            for dpcode in _CHANNEL_DPCODES
        ),
    }

    # Only the two power warning thresholds are writable, so they are the
    # only entries in `function`.
    assert set(device.function) == {"warn_power1", "warn_power2"}


def test_local_strategy_maps_dpids(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The device is local, so dpId reports must resolve to a status code."""
    device = create_device("cz_79a7z01v3n35kytb.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert set(device.local_strategy) == {
        *_CHANNEL_1_DPIDS,
        *_CHANNEL_2_DPIDS,
        _ALL_ENERGY_DPID,
    }
    for channel, dpids in ((1, _CHANNEL_1_DPIDS), (2, _CHANNEL_2_DPIDS)):
        for dpid, code in zip(dpids, _CHANNEL_DPCODES, strict=True):
            assert device.local_strategy[dpid]["status_code"] == code.format(
                n=channel
            )
    assert (
        device.local_strategy[_ALL_ENERGY_DPID]["status_code"] == "all_energy"
    )


def test_electricity_scaling(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Both channels report deci-volt, milli-amp and deci-watt."""
    device = create_device("cz_79a7z01v3n35kytb.json")
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


def test_energy_counter_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The daily and lifetime counters use milli-kWh and no sum report type."""
    device = create_device("cz_79a7z01v3n35kytb.json")
    filled_quirks_registry.initialise_device_quirk(device)

    for dpcode in (
        "total_energy1",
        "total_energy2",
        "today_acc_energy1",
        "today_acc_energy2",
        "all_energy",
    ):
        definition = device.status_range[dpcode]
        assert definition.report_type is None
        values = json.loads(definition.values)
        assert values["unit"] == "kWh"
        assert values["scale"] == 3


def test_device_state_enum_ranges_differ_per_channel(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Channel 1 reports `close` where channel 2 reports `idle`."""
    device = create_device("cz_79a7z01v3n35kytb.json")
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


def test_warning_threshold_limits(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Both channels expose read and write metadata for warning thresholds."""
    device = create_device("cz_79a7z01v3n35kytb.json")
    filled_quirks_registry.initialise_device_quirk(device)

    for code in ("warn_power1", "warn_power2"):
        assert (
            json.loads(device.status_range[code].values)
            == json.loads(device.function[code].values)
            == {"unit": "W", "min": 200, "max": 50000, "scale": 0, "step": 100}
        )
