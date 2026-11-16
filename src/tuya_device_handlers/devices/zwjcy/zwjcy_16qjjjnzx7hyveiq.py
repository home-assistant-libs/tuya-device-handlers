"""Recover moisture reports from the Wi-Fi Solar Soil Sensor."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="16qjjjnzx7hyveiq")
    # DP 111 is reported over MQTT but absent from the cloud local strategy.
    .add_dpid_integer(
        dpid=111,
        dpcode="humidity",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
