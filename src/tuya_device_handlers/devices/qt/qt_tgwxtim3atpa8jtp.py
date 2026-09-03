"""Quirk handler for RACER Pool Chlorinator (Electrolyseur).

Product ID: tgwxtim3atpa8jtp
Category: Overridden to 'js' (Water Purifier) to unlock pool properties.
"""

from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

# Racer Pool Chlorinator / Electrolyseur
(
    DeviceQuirk()
    .applies_to(product_id="tgwxtim3atpa8jtp")
    .override_category("js")
    # Main controls & modes
    .add_dpid_boolean(
        dpid=1, dpcode="switch", dpmode=DPMode.READ | DPMode.WRITE
    )
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["normal", "time"],
    )
    .add_dpid_boolean(
        dpid=3, dpcode="auto_boost", dpmode=DPMode.READ | DPMode.WRITE
    )
    # Production settings & timers
    .add_dpid_integer(
        dpid=4,
        dpcode="stepless_gear",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=20,
    )
    .add_dpid_integer(
        dpid=5,
        dpcode="production_time",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="h",
        min=0,
        max=24,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=6,
        dpcode="boost_time",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="h",
        min=0,
        max=96,
        scale=0,
        step=1,
    )
    # Counters & statistics
    .add_dpid_integer(
        dpid=7,
        dpcode="reverse_times",
        dpmode=DPMode.READ,
        unit="cycles",
        min=0,
        max=99999,
        scale=0,
        step=1,
    )
    # Pool cover settings
    .add_dpid_boolean(
        dpid=8, dpcode="pool_cover_enable", dpmode=DPMode.READ | DPMode.WRITE
    )
    .add_dpid_boolean(
        dpid=9, dpcode="pool_cover_switch", dpmode=DPMode.READ | DPMode.WRITE
    )
    # Pool parameters & scheduling
    .add_dpid_integer(
        dpid=10,
        dpcode="pool_size",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="m³",
        min=0,
        max=200,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=11,
        dpcode="start_time_hour",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="h",
        min=0,
        max=23,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=12,
        dpcode="start_time_min",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="min",
        min=0,
        max=59,
        scale=0,
        step=1,
    )
    .add_dpid_boolean(
        dpid=13, dpcode="dev_set", dpmode=DPMode.READ | DPMode.WRITE
    )
)
