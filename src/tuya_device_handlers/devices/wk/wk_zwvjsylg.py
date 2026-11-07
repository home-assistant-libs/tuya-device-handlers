"""Quirk for Thermostat Connecté (product_id zwvjsylg).

The cloud database only lists `eco` for the `mode` datapoint, but the
device also reports `comfort` and `off`, which are rejected as invalid
ENUM values. Redeclare the full range so Home Assistant accepts them.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/645
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="zwvjsylg")
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["eco", "comfort", "off"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
