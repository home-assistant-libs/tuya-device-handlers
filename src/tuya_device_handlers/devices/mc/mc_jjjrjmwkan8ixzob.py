"""Quirk for Tuya door sensor product jjjrjmwkan8ixzob.

The device reports `doorcontact_state` (dpid 1) as `opened`/`closed`, and
the cloud's local strategy maps those to the strings `"true"`/`"false"`
instead of booleans, so the door state is not usable as a binary sensor.

https://github.com/home-assistant/core/issues/193365
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(product_id="jjjrjmwkan8ixzob")
    .set_dpid_strategy_to_enum(
        dpid=1,
        dpcode="doorcontact_state",
        enum_mapping_map={"opened": True, "closed": False},
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
