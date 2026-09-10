"""Quirk for InverFlow / Aquagem Inverter Pool Pump (ircs2n82vgrozoew).

The Tuya OpenAPI cloud schema for category 'hwsb' (Outdoor Equipment) only
exposes DP 5 (cur_power) under standard functions, leaving control datapoints
unmapped in Home Assistant. This quirk defines the missing switch, mode,
speed, flow rate, and energy datapoints.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="ircs2n82vgrozoew",
        manufacturer="Aquagem",
        model="InverFlow Inverter Pool Pump",
        model_id="InverFlow",
    )
    # DP 105: Pump running / power switch
    .add_dpid_boolean(
        dpid=105,
        dpcode="switch",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    # DP 103: Operational mode
    .add_dpid_enum(
        dpid=103,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["MI", "AI", "backwash"],
    )
    # DP 111: Manual target power / speed percentage
    .add_dpid_integer(
        dpid=111,
        dpcode="speed_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="%",
        min=30,
        max=120,
        scale=0,
        step=5,
    )
    # DP 102: Actual reported motor speed percentage
    .add_dpid_integer(
        dpid=102,
        dpcode="speed_current",
        dpmode=DPMode.READ,
        unit="%",
        min=30,
        max=120,
        scale=0,
        step=1,
    )
    # DP 5: Real-time electrical power consumption
    .add_dpid_integer(
        dpid=5,
        dpcode="cur_power",
        dpmode=DPMode.READ,
        unit="W",
        min=0,
        max=3000,
        scale=0,
        step=1,
    )
    # DP 112: Real-time volume flow rate
    .add_dpid_integer(
        dpid=112,
        dpcode="flow_rate",
        dpmode=DPMode.READ,
        unit="gpm",
        min=0,
        max=1000,
        scale=0,
        step=1,
    )
    # DP 109: Cumulative energy consumption
    .add_dpid_integer(
        dpid=109,
        dpcode="add_ele",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=999999,
        scale=2,
        step=1,
        report_type="sum",
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
