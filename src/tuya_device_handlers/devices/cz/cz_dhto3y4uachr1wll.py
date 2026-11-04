"""Quirk for Double Digital Meter (product_id dhto3y4uachr1wll).

A two-channel DIN-rail current-transformer meter. Each channel reports its
own voltage, current, power and energy totals, plus a combined energy total
for both channels.

Tuya advertises no datapoints at all for this product: `function`,
`status_range` and `local_strategy` all come back empty, so Home Assistant
builds no entities and marks the device unsupported. Because the device is
`support_local`, an empty `local_strategy` also means the SDK drops every
incoming dpId report, which is why `status` stays empty as well.

The datapoint definitions below were taken from a diagnostics capture of the
same product_id in https://github.com/azerty9971/xtend_tuya/issues/990, and
the scales are confirmed against the physical device.

The device reports 24 datapoints in total (dpId 101-124). This quirk declares
the 15 that map to Home Assistant entities; the remaining 9 (`sync_request`,
`sync_response`, `add_ele1` / `add_ele2`, `today_energy_add1` /
`today_energy_add2`, `power_type1` / `power_type2` and `net_state`) are left
for a follow-up. The four `add_ele*` / `today_energy_add*` datapoints are
per-report increments rather than running totals -- the cloud's report-type
endpoint returns them with `report_type: sum` -- so `total_energy1` /
`total_energy2` are the cumulative counters used here.

See https://github.com/home-assistant/core/issues/176755.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="dhto3y4uachr1wll")
    # Channel 1
    .add_dpid_enum(
        dpid=103,
        dpcode="device_state1",
        dpmode=DPMode.READ,
        enum_range=["close", "monitor", "working", "warning"],
    )
    .add_dpid_integer(
        dpid=105,
        dpcode="cur_power1",
        dpmode=DPMode.READ,
        unit="W",
        min=0,
        max=2000000,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=106,
        dpcode="cur_current1",
        dpmode=DPMode.READ,
        unit="A",
        min=0,
        max=800000,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=107,
        dpcode="cur_voltage1",
        dpmode=DPMode.READ,
        unit="V",
        min=0,
        max=5000,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=108,
        dpcode="total_energy1",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=2147483647,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=109,
        dpcode="today_acc_energy1",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=2147483647,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=111,
        dpcode="warn_power1",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="W",
        min=200,
        max=50000,
        scale=0,
        step=100,
    )
    # Channel 2
    .add_dpid_enum(
        dpid=113,
        dpcode="device_state2",
        dpmode=DPMode.READ,
        enum_range=["idle", "monitor", "working", "warning"],
    )
    .add_dpid_integer(
        dpid=115,
        dpcode="cur_power2",
        dpmode=DPMode.READ,
        unit="W",
        min=0,
        max=2000000,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=116,
        dpcode="cur_current2",
        dpmode=DPMode.READ,
        unit="A",
        min=0,
        max=800000,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=117,
        dpcode="cur_voltage2",
        dpmode=DPMode.READ,
        unit="V",
        min=0,
        max=5000,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=118,
        dpcode="total_energy2",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=2147483647,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=119,
        dpcode="today_acc_energy2",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=2147483647,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=121,
        dpcode="warn_power2",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="W",
        min=200,
        max=50000,
        scale=0,
        step=100,
    )
    # Both channels combined
    .add_dpid_integer(
        dpid=123,
        dpcode="all_energy",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=2147483647,
        scale=3,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
