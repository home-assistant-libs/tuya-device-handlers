"""Quirk for Temperature/Humidity controller TY-WSD-B (datzwoplui1zao16).

Tuya advertises a generic socket profile for this device (switch_1,
countdown_1, cycle_time, fault) and does not expose its temperature and
humidity readings. The datapoints below have been retrieved from the
device property query.

See https://github.com/home-assistant-libs/tuya-device-handlers/issues/208
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="datzwoplui1zao16")
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
    .register(TUYA_QUIRKS_REGISTRY)
)
