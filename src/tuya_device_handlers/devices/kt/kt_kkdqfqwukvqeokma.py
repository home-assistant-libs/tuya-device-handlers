"""Quirk for July window air conditioner (product_id KkdQFqwukvqeoKMa).

The cloud definition advertises `hot` (heat) in the `mode` enum, but this
is a cooling-only window unit, so Home Assistant offers a heat mode the
device cannot perform. The device's thing model describes the modes as
auto (feel), cold, hot, wet (dry) and wind (fan only).

The thing model (Tuya end-user API) also declares ECO mode (DP 8,
`mode_ECO`) and sleep (DP 101, `sleep`) as writable booleans, but the
cloud does not advertise them to the device sharing API. They are added
under the standard `mode_eco` and `sleep` codes.

This quirk removes `hot` from the mode range and adds the ECO and sleep
datapoints.
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
    .add_dpid_boolean(
        dpid=8,
        dpcode="mode_eco",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    .add_dpid_boolean(
        dpid=101,
        dpcode="sleep",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
