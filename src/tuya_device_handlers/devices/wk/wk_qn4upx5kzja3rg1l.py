"""Quirk for Thermostat-ST300 (product_id qn4upx5kzja3rg1l).

The cloud database only lists `auto` for the `mode` datapoint, but the
device also reports `heat`, which is rejected as an invalid ENUM value.
Redeclare the range so Home Assistant accepts it.

Other values (such as `cold` or `wind` on this fan-coil model) are not
confirmed yet, so they are not declared.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/651
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="qn4upx5kzja3rg1l", model_id="ST300")
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "heat"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
