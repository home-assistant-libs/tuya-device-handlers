"""Quirk for Comfort Zone Tower Fan (CZTF423S)."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

# Define the structured quirk using the fluent builder pattern
(
    DeviceQuirk()
    .applies_to(
        product_id="xwv3jifdbhbolgh3",
        manufacturer="Comfort Zone",
        model="Tower Fan",
        model_id="CZTF423S",
    )
    # DP 2: Expand fan mode range to include "normal"
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["normal", "nature", "sleep"],
    )
    # DP 22: Expand countdown timer options beyond 6h to 12h
    .add_dpid_enum(
        dpid=22,
        dpcode="countdown_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=[
            "cancel",
            "1h",
            "2h",
            "3h",
            "4h",
            "5h",
            "6h",
            "7h",
            "8h",
            "9h",
            "10h",
            "11h",
            "12h",
        ],
    )
    # Register quirk with global handler registry
    .register(TUYA_QUIRKS_REGISTRY)
)
