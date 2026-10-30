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
        unit="°C",
        min=0,
        max=850,
        scale=1,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
