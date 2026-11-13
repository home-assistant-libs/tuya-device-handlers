"""Quirk for HQ-JS2326 humidifier (product_id tfziezfrkj6s8frq).

Tuya advertises no datapoints for this humidifier: function, status_range,
local_strategy and status all arrive empty, so Home Assistant cannot build
any entity for it.

The device's thing model (from the Tuya end-user API) declares these
datapoints, which this quirk adds under their cloud codes:
  DP 2  -> switch_spray (bool, rw): power
  DP 13 -> humidity_set (integer 40-90 %, step 5, rw): target humidity
  DP 14 -> humidity_current (integer 0-100 %, ro): current humidity
  DP 16 -> sleep (bool, rw): sleep mode
  DP 23 -> level (enum level_1..level_6, rw): mist level

Commands are sent through the Tuya cloud by DPCode, so the cloud codes are
kept unchanged.

Limitation: the Tuya cloud rejects every command for this product with
error `2008` (tested with switch_spray, humidity_set, sleep and level), so
the added datapoints are effectively read-only in Home Assistant. They are
still declared writable so the entities match the device's capabilities.

The thing model also declares datapoints that Home Assistant has no
humidifier mapping for, so they are not added here: switch_led (DP 5, the
UV lamp), countdown_left (DP 20), fault (DP 22, bitmap lack_water/clear),
time (DP 101, run hours), switch_led_2 (DP 102, mood light), swing (DP 103),
clean_time (DP 104), countdown_enable (DP 106), set_time (DP 107) and
switch_hun (DP 108, constant-humidity mode).
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="tfziezfrkj6s8frq")
    .add_dpid_boolean(
        dpid=2,
        dpcode="switch_spray",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    .add_dpid_integer(
        dpid=13,
        dpcode="humidity_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="%",
        min=40,
        max=90,
        scale=0,
        step=5,
    )
    .add_dpid_integer(
        dpid=14,
        dpcode="humidity_current",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .add_dpid_boolean(
        dpid=16,
        dpcode="sleep",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    .add_dpid_enum(
        dpid=23,
        dpcode="level",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=[
            "level_1",
            "level_2",
            "level_3",
            "level_4",
            "level_5",
            "level_6",
        ],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
