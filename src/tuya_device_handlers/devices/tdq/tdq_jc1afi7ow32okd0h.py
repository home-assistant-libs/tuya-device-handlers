"""Quirk for T & H Sensor with external probe (product_id jc1afi7ow32okd0h).

Tuya does not advertise any datapoints for this device.
They have been retrieved from the Tuya Developer Portal.

See https://github.com/home-assistant/core/issues/163205.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="jc1afi7ow32okd0h")
    .override_category("wsdcg")
    .add_dpid_integer(
        dpid=101,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="℃",
        min=-200,
        max=600,
        scale=1,
        step=1,
    )
    .add_dpid_integer(
        dpid=102,
        dpcode="humidity_value",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .add_dpid_enum(
        dpid=103,
        dpcode="battery_state",
        dpmode=DPMode.READ,
        enum_range=["low", "middle", "high"],
    )
    .add_dpid_integer(
        dpid=106,
        dpcode="ext_temp",
        dpmode=DPMode.READ,
        unit="℃",
        min=-200,
        max=600,
        scale=1,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
