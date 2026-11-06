"""Quirk for L15 Ultra robot vacuum (oaelsi57ejdiavfh).

The cloud function list omits `closed` for the `cistern` datapoint and
`goto_charge` for the `mode` datapoint, but the device reports both. Redeclare
the full enum ranges so Home Assistant accepts the values.

See https://github.com/home-assistant-libs/tuya-device-handlers/issues/642
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="oaelsi57ejdiavfh")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["smart", "zone", "pose", "part", "goto_charge"],
    )
    .add_dpid_enum(
        dpid=10,
        dpcode="cistern",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["closed", "low", "middle", "high"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
