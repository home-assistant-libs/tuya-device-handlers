from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

TUYA_QUIRKS_REGISTRY.register(
    DeviceQuirk()
    .product_id("eb414680be46558e014mtb")
    .name("TOWER FAN (CZTF423S)")
    .datapoint(1, code="switch", mode=DPMode.READ_WRITE)
    .datapoint(
        2, 
        code="mode", 
        mode=DPMode.READ_WRITE, 
        values=["normal", "nature", "sleep"]
    )
    .datapoint(
        3, 
        code="speed", 
        mode=DPMode.READ_WRITE, 
        values={"min": 1, "max": 5, "step": 1}
    )
    .datapoint(5, code="switch_horizontal", mode=DPMode.READ_WRITE)
    .datapoint(13, code="status", mode=DPMode.READ_ONLY)
    .datapoint(
        22,
        code="countdown",
        mode=DPMode.READ_WRITE,
        values=["cancel", "1h", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "10h", "11h", "12h"]
    )
)
