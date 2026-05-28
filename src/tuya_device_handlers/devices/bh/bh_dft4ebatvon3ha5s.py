"""Quirk for Tuya smart kettle product dft4ebatvon3ha5s.

The Tuya cloud product catalog declares only ["85","90"] for
temp_setting_quick_c (dpid 4), but the device physically supports
["80","85","90","95","100"]. This was confirmed via:
- physical button testing (all values lit and started heating)
- local LAN (tinytuya) commands accepted and echoed by firmware
- cloud MQTT push reports all values when set physically
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="dft4ebatvon3ha5s",
        manufacturer="Anko",
        model="Smart kettle",
        model_id="LD-K3068",
    )
    .add_dpid_enum(
        dpid=4,
        dpcode="temp_setting_quick_c",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["80", "85", "90", "95", "100"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
