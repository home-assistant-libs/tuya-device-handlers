"""Quirk for Smart Pet Feeder PP001 with camera (product_id 8zrzjldq07tlxnlv).

Tuya declares this pet feeder under the camera category ('sp') and only
advertises the camera datapoints (indicator, night vision, recording, SD card,
restart). The feeder datapoints are missing from function, status_range and
local_strategy, so their MQTT reports are dropped.

The device does report them over MQTT (datapoint ids from the device's cloud
thing model):
  DP 238 -> battery_status (enum high/low/no)
  DP 239 -> food_storage_status (enum full/less/lack)
  DP 240 -> feed_block_status (bool)
  DP 241 -> feed_stuck_status (bool)
  DP 243 -> manual_feed_report (portions dispensed by a manual feed)
  DP 244 -> auto_feed_report (portions dispensed by a scheduled feed)
  DP 246 -> feed_report (portions dispensed)

The thing model declares scale 1 for DP 243 and DP 244, but the device reports
plain portions on them (1 after a 1-portion feed), matching DP 246, so they are
added with scale 0.

The feed command (DP 245, feed_publish) is not added: the Smart Life cloud
rejects it for this product with error 2008 (command or value not supported).
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="8zrzjldq07tlxnlv")
    .add_dpid_enum(
        dpid=238,
        dpcode="battery_status",
        dpmode=DPMode.READ,
        enum_range=["high", "low", "no"],
    )
    .add_dpid_enum(
        dpid=239,
        dpcode="food_storage_status",
        dpmode=DPMode.READ,
        enum_range=["full", "less", "lack"],
    )
    .add_dpid_boolean(
        dpid=240,
        dpcode="feed_block_status",
        dpmode=DPMode.READ,
    )
    .add_dpid_boolean(
        dpid=241,
        dpcode="feed_stuck_status",
        dpmode=DPMode.READ,
    )
    .add_dpid_integer(
        dpid=243,
        dpcode="manual_feed_report",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=200,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=244,
        dpcode="auto_feed_report",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=200,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=246,
        dpcode="feed_report",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=99,
        scale=0,
        step=1,
        report_type="sum",
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
