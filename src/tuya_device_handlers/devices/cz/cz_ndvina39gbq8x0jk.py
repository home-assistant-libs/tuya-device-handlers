"""Quirk for Konyks Priska Max 3 FR (ndvina39gbq8x0jk).

DP 40 (``light_mode``) is missing value: on.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="ndvina39gbq8x0jk",
        manufacturer="Konyks",
        model="Priska Max 3 FR",
    )
    .add_dpid_enum(
        dpid=40,
        dpcode="light_mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["relay", "pos", "none", "on"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
