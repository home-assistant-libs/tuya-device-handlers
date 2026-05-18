"""Tuya quirk for Convector Heater with Wi-Fi.

Product ID: 8axigg3icem6telp
Category: qn (heater)

Level mapping (DP 5):
    "1" = Low   (750W)
    "2" = Medium (1250W)
    "3" = High  (2000W)
    "4" = Off   (0W)   ← also set automatically when mode="off"

Mode mapping (DP 4):
    "smart" = Anti-frost mode
    "auto"  = Auto mode
    "off"   = Off mode (also forces level to "4" on the device side)

DP 9 ("anion" in stock firmware) is relabelled "turbo" — it toggles the fan.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="8axigg3icem6telp")
    # Switch (DP 1)
    .add_dpid_boolean(
        dpid=1,
        dpcode="switch",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    # Temperature setpoint (DP 2)
    .add_dpid_integer(
        dpid=2,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="°C",
        min=5,
        max=37,
        scale=0,
        step=1,
    )
    # Current temperature (DP 3)
    .add_dpid_integer(
        dpid=3,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="°C",
        min=-20,
        max=50,
        scale=0,
        step=1,
        report_type="unknown",  # FIX: was "un_known" (typo)
    )
    # Mode (DP 4)
    # "smart" = Anti-frost, "auto" = Auto, "off" = Off (also sets level="4")
    .add_dpid_enum(
        dpid=4,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["smart", "auto", "off"],
    )
    # Level (DP 5) — power level / heat output
    # "1"=Low (750W), "2"=Medium (1250W), "3"=High (2000W), "4"=Off (0W)
    .add_dpid_enum(
        dpid=5,
        dpcode="level",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["1", "2", "3", "4"],
    )
    # Turbo / fan boost (DP 9)
    # Stock firmware calls this "anion" / "Ionisator"; correct name is "turbo".
    .remove_dpid(dpid=9, dpcode="anion")
    .add_dpid_boolean(
        dpid=9,
        dpcode="turbo",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    # Countdown timer (DP 12)
    .add_dpid_integer(
        dpid=12,
        dpcode="countdown_left",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="s",
        min=0,
        max=86400,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
