"""Quirk for July window air conditioner (product_id KkdQFqwukvqeoKMa).

The cloud definition advertises `hot` (heat) in the `mode` enum, but this
is a cooling-only window unit, so Home Assistant offers a heat mode the
device cannot perform. The device's thing model describes the modes as
auto (feel), cold, hot, wet (dry) and wind (fan only).

This quirk removes `hot` from the mode range.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="KkdQFqwukvqeoKMa")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "cold", "wet", "wind"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
