from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="vx9tbbzhfmcc0f3k")

    .add_dpid_integer(
        dpid=3,
        dpcode="temperature_f",
        dpmode=DPMode.READ,
        unit="°F",
        min=32,
        max=99,
        scale=0,
        step=1,
    )

    .add_dpid_integer(
        dpid=5,
        dpcode="c_temperature",
        dpmode=DPMode.READ,
        unit="°C",
        min=0,
        max=50,
        scale=0,
        step=1,
    )

    .add_dpid_integer(
        dpid=6,
        dpcode="f_temperature",
        dpmode=DPMode.READ,
        unit="°F",
        min=32,
        max=122,
        scale=0,
        step=1,
    )

    .register(TUYA_QUIRKS_REGISTRY)
)