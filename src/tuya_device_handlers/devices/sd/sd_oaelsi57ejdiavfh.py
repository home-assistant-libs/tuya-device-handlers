"""Quirk for L15 Ultra robot vacuum (product_id oaelsi57ejdiavfh).

The cloud `function` schema only lists `low`/`middle`/`high` for the
`cistern` datapoint, but the device also reports `closed` (water tank
removed or empty), which is rejected as an invalid ENUM value. The
local strategy and status_range already include `closed`; redeclare
the full range so Home Assistant accepts it.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/642
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="oaelsi57ejdiavfh")
    .add_dpid_enum(
        dpid=10,
        dpcode="cistern",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["closed", "low", "middle", "high"],
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
