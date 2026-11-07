"""Quirk for WiFi Thermostat (product_id r2ilemqbtocmulgb).

DP 24 (``temp_current``) is advertised as scale 0, range 0-50, but the
device reports tenths of a degree (e.g. 125 = 12.5 °C), consistent with
its ``temp_set`` datapoint (scale 1). Readings above 50 are therefore
rejected and the current temperature is never shown.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="r2ilemqbtocmulgb")
    .add_dpid_integer(
        dpid=24,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="℃",
        min=0,
        max=500,
        scale=1,
        step=5,
        report_type="sum",
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
