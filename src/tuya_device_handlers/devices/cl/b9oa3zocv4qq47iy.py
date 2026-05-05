"""Quirk for A-OK AM45 Plus Wi-Fi tubular motor (product_id b9oa3zocv4qq47iy).

This device advertises ``percent_state`` in its ``status_range`` but never
pushes updates for that DP over MQTT, so the default CL mapping (which
prefers ``percent_state``) leaves ``current_position`` stuck at its startup
value while the blind physically moves. Suppress ``percent_state`` so the
default mapping falls back to ``percent_control``, which this device does
push.

See https://github.com/home-assistant/core/issues/168493.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk

(
    DeviceQuirk()
    .applies_to(
        product_id="b9oa3zocv4qq47iy",
        manufacturer="A-OK",
        model="Tubular motor",
        model_id="AM45 Plus Wi-Fi",
    )
    .remove_dpid(dpid=3, dpcode="percent_state")
    .register(TUYA_QUIRKS_REGISTRY)
)
