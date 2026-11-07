"""Quirk for Konyks Priska Duo FR (avriaapskyik4eaa).

DP 40 (``light_mode``) is missing value: on.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="avriaapskyik4eaa",
        manufacturer="Konyks",
        model="Priska Duo FR",
    )
    .add_dpid_enum(
        dpid=40,
        dpcode="light_mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["relay", "pos", "none", "on"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
