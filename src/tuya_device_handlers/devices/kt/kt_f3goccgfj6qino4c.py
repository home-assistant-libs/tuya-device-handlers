"""Quirk for Skyworth air conditioner (product_id f3goccgfj6qino4c).

The cloud database does not list `strong` for the `fan_speed_enum`
datapoint, nor `wind` for the `mode` datapoint, but the device reports
both, so they are rejected as invalid ENUM values. Redeclare the full
ranges so Home Assistant accepts them.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/318
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="f3goccgfj6qino4c")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "cold", "wet", "heat", "fan", "wind"],
    )
    .add_dpid_enum(
        dpid=5,
        dpcode="fan_speed_enum",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=[
            "auto",
            "low",
            "low_mid",
            "mid",
            "mid_high",
            "high",
            "mute",
            "turbo",
            "strong",
        ],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
