"""Quirk for S1 robot vacuum (product_id txitlmevigna7hyc).

The cloud database does not list `Random_Clean` for the `status`
datapoint, but the device reports it, so it is rejected as an invalid
ENUM value. Redeclare the full range so Home Assistant accepts it.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/548
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="txitlmevigna7hyc")
    .add_dpid_enum(
        dpid=5,
        dpcode="status",
        dpmode=DPMode.READ,
        enum_range=[
            "standby",
            "smart_clean",
            "wall_clean",
            "spot_clean",
            "mop_clean",
            "Random_Clean",
            "goto_charge",
            "charging",
            "charge_done",
            "paused",
        ],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
