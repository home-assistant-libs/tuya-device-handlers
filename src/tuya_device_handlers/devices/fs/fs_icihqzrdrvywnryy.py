"""Quirk for Klassfan ceiling fan (product_id icihqzrdrvywnryy).

The cloud database only lists `sleep`/`nature` for the `mode` datapoint,
but the device also reports `normal`, and `temprature` (sic, firmware
spelling) for its temperature-driven fan speed mode. Both are rejected as
invalid ENUM values. Redeclare the full range so Home Assistant displays the
current mode as a preset.

The Tuya cloud still rejects commands to set `normal` or `temprature`, as
they are not in its own definition, so only reading them is fixed for now.

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
        enum_range=["normal", "sleep", "nature", "temprature"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
