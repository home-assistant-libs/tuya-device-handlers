"""Quirk for Temperature/Humidity sensor (product_id x3o8epevyeo3z3oa).

Tuya does not advertise any datapoints for this device.
They have been retrieved from the Tuya Developer Portal.

See https://github.com/home-assistant/core/issues/163360.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="x3o8epevyeo3z3oa")
    .add_dpid_enum(
        dpid=20,
        dpcode="temp_unit_convert",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["c", "f"],
    )
    .add_dpid_integer(
        dpid=27,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="℃",
        min=-200,
        max=600,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=46,
        dpcode="humidity_value",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .add_dpid_enum(
        dpid=101,
        dpcode="battery_state",
        dpmode=DPMode.READ,
        enum_range=["low", "middle", "high"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
