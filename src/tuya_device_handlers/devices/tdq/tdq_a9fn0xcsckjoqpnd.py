"""Quirk for Contact sensor 001D02T1-3S (product_id a9fn0xcsckjoqpnd).

Tuya declares this door sensor under the wrong category ('tdq' = breaker,
instead of 'mcs' = door/window sensor) and advertises no datapoints at all:
function, status_range and local_strategy all arrive empty, so Home Assistant
cannot build any entity for it.

The device does report over MQTT:
  DP 101 -> doorcontact_state (bool)
  DP 102 -> battery_state (enum low/middle/high)

Reported upstream in home-assistant/core#159399.
Mirrors devices/tdq/tdq_p6sqiuesvhmhvv4f.py, which fixes the identical
defect on a sibling contact sensor.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="a9fn0xcsckjoqpnd")
    .override_category("mcs")
    .add_dpid_boolean(
        dpid=101,
        dpcode="doorcontact_state",
        dpmode=DPMode.READ,
    )
    .add_dpid_enum(
        dpid=102,
        dpcode="battery_state",
        dpmode=DPMode.READ,
        enum_range=["low", "middle", "high"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
