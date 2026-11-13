"""Quirk for WDH-870FW dehumidifier (product_id 28ts8zanupz0yytl).

The cloud database only lists `low`/`high` for the `fan_speed_enum`
datapoint, but the device also reports `med`, which is rejected as an
invalid ENUM value. Redeclare the full range so Home Assistant accepts it.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/537
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="28ts8zanupz0yytl")
    .add_dpid_enum(
        dpid=4,
        dpcode="fan_speed_enum",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["low", "med", "high"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
