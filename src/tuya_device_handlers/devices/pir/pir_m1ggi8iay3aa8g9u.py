from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="m1ggi8iay3aa8g9u")
    .add_dpid_integer(
        dpid=8,
        dpcode="humidity_value",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=11,
        dpcode="illuminance_value",
        dpmode=DPMode.READ,
        unit="lx",
        min=0,
        max=100000,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
