"""Quirk for Smart fan (jaw7hqx0ulo3bkbi).

Tuya declares this ceiling fan light under the wrong category ('xdd' = ceiling
light, instead of 'fsd' = ceiling fan light) and omits the fan datapoints, so
Home Assistant does not create a fan entity for it.

Overrides the category to 'fsd' and adds the missing fan datapoints:
  DP 101 -> fan_switch (bool)
  DP 102 -> fan_mode (enum fresh/nature)
  DP 103 -> fan_speed (integer 1..6)
  DP 104 -> fan_direction (enum forward/reverse)

See https://github.com/home-assistant-libs/tuya-device-handlers/issues/478.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

RW_MODE = DPMode.READ | DPMode.WRITE

(
    DeviceQuirk()
    .applies_to(product_id="jaw7hqx0ulo3bkbi")
    .override_category("fsd")
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
    .register(TUYA_QUIRKS_REGISTRY)
)
