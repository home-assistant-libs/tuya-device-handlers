"""Quirk for Vital+ Ice Bath Pro chiller (product_id urzivdhumrwfakie).

The Tuya cloud reports this device as category 'ktkzq' (Air conditioner controller)
which HA has no entity mappings for. This quirk overrides the category to 'wk'
(thermostat) so HA creates climate + switch entities from the existing dpcodes.

Data points:
  DP 2   temp_set      Integer  3-45°C (scale 0)  - target temperature
  DP 3   temp_current  Integer  -40 to 100°C (scale 1) - current water temp
  DP 7   child_lock    Boolean  - child lock
  DP 108 power_switch  Boolean  - chiller on/off (mapped to 'switch' for climate)
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(
        product_id="urzivdhumrwfakie",
        manufacturer="Vital+",
        model="Ice Bath Pro",
    )
    .override_category("wk")
    # DP 2: temp_set (already in function/status_range, but ensure it's writable)
    .add_dpid_integer(
        dpid=2,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℃", min=3, max=45, scale=0, step=1,
    )
    # DP 3: temp_current (read-only, scale 1 means divide by 10)
    .add_dpid_integer(
        dpid=3,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="℃", min=-400, max=1000, scale=1, step=1,
    )
    # DP 7: child_lock (read/write boolean)
    .add_dpid_boolean(
        dpid=7,
        dpcode="child_lock",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    # DP 108: power_switch -> mapped as 'switch' so climate entity has on/off
    .add_dpid_boolean(
        dpid=108,
        dpcode="switch",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
