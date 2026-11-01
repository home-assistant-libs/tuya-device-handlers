"""Quirk for Beok TOL47WIFI-WPB thermostat (product_id 22m2ytawuenfen5b).

The cloud database only lists `auto` for the `mode` datapoint, but the
device also reports `home` and `temporary`, which are rejected as invalid
ENUM values. Redeclare the full range so Home Assistant accepts them.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/525
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="22m2ytawuenfen5b")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["home", "auto", "temporary"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
