"""Quirk for Thermostat (product_id lmtejj3f4kafi2k1).

The cloud doesn't declare DP 105, but the device reports the current room
temperature on it in tenths of a degree (e.g. 265 = 26.5 °C), so the climate
entity never shows a current temperature.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/691
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="lmtejj3f4kafi2k1")
    .add_dpid_integer(
        dpid=105,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="℃",
        min=0,
        max=850,
        scale=1,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
