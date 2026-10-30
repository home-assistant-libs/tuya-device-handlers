"""Quirk for ALDI KT2217AC smart kettle product xo5wnj56ip8haw1s.

The catalog declares `work_type` (dpid 9) with the single value
`boiling_quick`, but the firmware always reports `heating_quick`. Home
Assistant rejects that value, so the work mode select stays at `unknown`
and every report logs an invalid ENUM warning.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(
        product_id="xo5wnj56ip8haw1s",
        manufacturer="Tuya",
        model="ALDI: KT2217AC",
    )
    .set_dpid_strategy_to_enum(
        dpid=9,
        dpcode="work_type",
        enum_mapping_map={"heating_quick": "boiling_quick"},
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
