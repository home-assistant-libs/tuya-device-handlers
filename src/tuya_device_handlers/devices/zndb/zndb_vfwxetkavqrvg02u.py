"""Quirk for PC311_W_TY dual-clamp energy meter (vfwxetkavqrvg02u).

The cloud schema only lists the total datapoints. Declare the missing
per-circuit, clamp direction, reactive power and frequency datapoints
(dpids 101-117).

Ranges are taken from the device model returned by the Tuya cloud.
The cloud reports power in kW and reactive power in kVar, both with
scale 3, which is the same raw value as W and var with scale 0.

Per-circuit datapoints follow Home Assistant Core's <measurement><channel>
naming pattern (total_energy1/2, reverse_energy1/2, cur_current1/2,
cur_power1/2, power_factor1/2, reactive_power1/2, ct_direction1/2).

See https://github.com/home-assistant-libs/tuya-device-handlers/issues/626
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="vfwxetkavqrvg02u", model_id="PC311_W_TY")
    .add_dpid_integer(
        dpid=101,
        dpcode="total_energy1",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=999999999,
        scale=2,
        step=1,
    )
    .add_dpid_integer(
        dpid=102,
        dpcode="reverse_energy1",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=999999999,
        scale=2,
        step=1,
    )
    .add_dpid_integer(
        dpid=103,
        dpcode="total_energy2",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=999999999,
        scale=2,
        step=1,
    )
    .add_dpid_integer(
        dpid=104,
        dpcode="reverse_energy2",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=999999999,
        scale=2,
        step=1,
    )
    .add_dpid_integer(
        dpid=105,
        dpcode="cur_current",
        dpmode=DPMode.READ,
        unit="A",
        min=0,
        max=1000000000,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=106,
        dpcode="cur_voltage",
        dpmode=DPMode.READ,
        unit="V",
        min=0,
        max=1000000,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=107,
        dpcode="cur_current1",
        dpmode=DPMode.READ,
        unit="A",
        min=0,
        max=1000000,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=108,
        dpcode="cur_power1",
        dpmode=DPMode.READ,
        unit="W",
        min=-1000000000,
        max=1000000000,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=109,
        dpcode="power_factor1",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=100,
        scale=2,
        step=1,
    )
    .add_dpid_integer(
        dpid=110,
        dpcode="cur_current2",
        dpmode=DPMode.READ,
        unit="A",
        min=0,
        max=1000000,
        scale=3,
        step=1,
    )
    .add_dpid_integer(
        dpid=111,
        dpcode="cur_power2",
        dpmode=DPMode.READ,
        unit="W",
        min=-1000000000,
        max=1000000000,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=112,
        dpcode="power_factor2",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=100,
        scale=2,
        step=1,
    )
    .add_dpid_boolean(
        dpid=113,
        dpcode="ct_direction1",
        dpmode=DPMode.READ,
    )
    .add_dpid_boolean(
        dpid=114,
        dpcode="ct_direction2",
        dpmode=DPMode.READ,
    )
    .add_dpid_integer(
        dpid=115,
        dpcode="reactive_power1",
        dpmode=DPMode.READ,
        unit="var",
        min=-1000000000,
        max=1000000000,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=116,
        dpcode="reactive_power2",
        dpmode=DPMode.READ,
        unit="var",
        min=-1000000000,
        max=1000000000,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=117,
        dpcode="supply_frequency",
        dpmode=DPMode.READ,
        unit="Hz",
        min=0,
        max=10000,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
