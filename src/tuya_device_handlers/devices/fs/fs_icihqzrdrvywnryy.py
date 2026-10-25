"""Quirk for Klassfan ceiling fan (product_id icihqzrdrvywnryy).

The cloud database only lists `sleep`/`nature` for the `mode` datapoint,
but the device also reports `temprature` (sic, firmware spelling) for its
temperature-driven fan speed mode, which is rejected as an invalid ENUM
value. Redeclare the full range so Home Assistant exposes it as a preset.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/623
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="icihqzrdrvywnryy")
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["sleep", "nature", "temprature"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
