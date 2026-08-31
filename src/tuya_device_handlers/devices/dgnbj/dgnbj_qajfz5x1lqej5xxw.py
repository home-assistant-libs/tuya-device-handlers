"""Quirk for the Tuya "WiFi smart online 5 in 1 tester" (qajfz5x1lqej5xxw).

Category ``dgnbj``. The cloud data model for this device only exposes
``temp_current`` (dp 8), even though the device also measures pH (and, with a
wet and calibrated probe, EC / salinity / specific gravity). The extra values
are reported over MQTT on datapoints that are missing from the cloud data
model, so the sharing SDK drops them as "unknown dpId" and Home Assistant
never builds the corresponding entities.

This quirk redeclares the pH datapoint (dp 102) so Home Assistant builds the
pH sensor. The scale was confirmed against the Tuya Smart Life app
(raw value 939 -> 9.39 pH).
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="qajfz5x1lqej5xxw")
    .add_dpid_integer(
        dpid=102,
        dpcode="ph_current",
        dpmode=DPMode.READ,
        unit="ph",
        min=0,
        max=1400,
        scale=2,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
