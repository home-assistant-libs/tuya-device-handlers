"""Quirk for TURBRO Beluga B58V pool heat pump (product_id zqrzsid4zllmowtt).

The cloud database only lists `auto` for the `mode` datapoint, but the
device also reports `make_hot`, which is rejected as an invalid ENUM
value. Redeclare the range with the confirmed values so Home Assistant
accepts them.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/663
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="zqrzsid4zllmowtt")
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "make_hot"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
