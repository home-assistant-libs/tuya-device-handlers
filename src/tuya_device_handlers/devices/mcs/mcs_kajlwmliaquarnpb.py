"""Quirk for Stitch Door/Window Sensor (product_id KajlwMlIaQUARNpb).

Tuya advertises no datapoints for this door sensor: function, status_range
and local_strategy all arrive empty, so Home Assistant cannot build any
entity for it.

The device's thing model (from the Tuya end-user API) declares:
  DP 101 -> switch (bool, door open state)
  DP 102 -> TamperedAlarm (bool)
  DP 103 -> Battery (integer 0-100 %, step 10)

DP 101 keeps its cloud code `switch`, which Home Assistant already maps to a
door binary sensor for this category. The tamper and battery codes are
non-standard, so they are mapped to `temper_alarm` and `battery_percentage`.

Reported in home-assistant-libs/tuya-device-handlers#740.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="KajlwMlIaQUARNpb")
    .add_dpid_boolean(
        dpid=101,
        dpcode="switch",
        dpmode=DPMode.READ,
    )
    .add_dpid_boolean(
        dpid=102,
        dpcode="temper_alarm",
        dpmode=DPMode.READ,
    )
    .add_dpid_integer(
        dpid=103,
        dpcode="battery_percentage",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=10,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
