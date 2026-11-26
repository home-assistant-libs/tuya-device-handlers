"""Quirk for Smart fan (jaw7hqx0ulo3bkbi).

Adds missing datapoints for light control (DP 20 switch_led, DP 22 bright_value,
DP 106 cct, DP 107 bright_value2) and fan control (DP 101 fan_switch,
DP 102 fan_mode, DP 103 fan_speed, DP 104 fan_direction,
DP 105 fan_countdown_left).

See https://github.com/home-assistant-libs/tuya-device-handlers/issues/478.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

RW_MODE = DPMode.READ | DPMode.WRITE

(
    DeviceQuirk()
    .applies_to(product_id="jaw7hqx0ulo3bkbi")
    .add_dpid_boolean(
        dpid=20,
        dpcode="switch_led",
        dpmode=RW_MODE,
    )
    .add_dpid_integer(
        dpid=22,
        dpcode="bright_value",
        dpmode=RW_MODE,
        unit="",
        min=10,
        max=1000,
        scale=0,
        step=1,
    )
    .add_dpid_boolean(
        dpid=101,
        dpcode="fan_switch",
        dpmode=RW_MODE,
    )
    .add_dpid_enum(
        dpid=102,
        dpcode="fan_mode",
        dpmode=RW_MODE,
        enum_range=["fresh", "nature"],
    )
    .add_dpid_integer(
        dpid=103,
        dpcode="fan_speed",
        dpmode=RW_MODE,
        unit="",
        min=1,
        max=6,
        scale=0,
        step=1,
    )
    .add_dpid_enum(
        dpid=104,
        dpcode="fan_direction",
        dpmode=RW_MODE,
        enum_range=["forward", "reverse"],
    )
    .add_dpid_integer(
        dpid=105,
        dpcode="fan_countdown_left",
        dpmode=RW_MODE,
        unit="min",
        min=0,
        max=540,
        scale=0,
        step=1,
    )
    .add_dpid_enum(
        dpid=106,
        dpcode="cct",
        dpmode=RW_MODE,
        enum_range=["warm", "Neutral", "white"],
    )
    .add_dpid_integer(
        dpid=107,
        dpcode="bright_value2",
        dpmode=RW_MODE,
        unit="%",
        min=1,
        max=100,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
