"""Quirk for E30 robot vacuum (product_id qv442aix6nlsktmi).

The cloud database does not list `Charge_Comp` for the `status`
datapoint, but the device reports it, so it is rejected as an invalid
ENUM value. Redeclare the full range so Home Assistant accepts it.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/402
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="qv442aix6nlsktmi")
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
            "goto_charge",
            "charging",
            "charge_done",
            "Charge_Comp",
            "paused",
            "cleaning",
            "zone_clean",
            "part_clean",
            "pick_zone_clean",
            "goto_pos",
            "pos_arrived",
            "pos_unarrive",
            "sleep",
        ],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
