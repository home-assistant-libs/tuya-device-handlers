"""Quirk for the Tuya "WiFi smart online 5 in 1 tester" (qajfz5x1lqej5xxw).

Category ``dgnbj``. The cloud data model for this device only exposes
``temp_current`` (dp 8), even though the device also measures pH (and, with a
wet and calibrated probe, EC / salinity / specific gravity). The extra values
are reported over MQTT on datapoints that are missing from the cloud data
model, so the sharing SDK drops them as "unknown dpId" and Home Assistant
never builds the corresponding entities.

This quirk redeclares pH (dp 102) and electrical conductivity (dp 110)
so Home Assistant builds both sensors. The raw pH value 939 corresponds
to pH 9.39. The raw conductivity value 1608 matched 1608 µS/cm in the
Tuya Smart app.
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
    .add_dpid_integer(
        dpid=110,
        dpcode="ec_current",
        dpmode=DPMode.READ,
        unit="µS/cm",
        min=0,
        max=2147483647,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
