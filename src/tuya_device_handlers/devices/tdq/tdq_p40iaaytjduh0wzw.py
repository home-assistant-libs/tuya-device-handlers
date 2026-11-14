"""Quirk for 2CH Wi-Fi Smart Energy Monitor (p40iaaytjduh0wzw).

Tuya only exposes Channel 1 (cur_current, cur_power, cur_voltage, add_ele)
in the standard profile for category tdq. Channel 2 datapoints
(cur_current2, cur_power2, cur_voltage2, add_ele2) exist on the device
but are not mapped by default. This quirk forces the correct mapping
so both channels become available in Home Assistant.
"""
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="p40iaaytjduh0wzw")
    # Channel 2 Current
    .add_dpid_integer(
        dpid=18,
        dpcode="cur_current2",
        dpmode=DPMode.READ,
        unit="mA",
        min=0,
        max=200000,
        scale=0,
        step=1,
    )
    # Channel 2 Power
    .add_dpid_integer(
        dpid=19,
        dpcode="cur_power2",
        dpmode=DPMode.READ,
        unit="W",
        min=0,
        max=500000,
        scale=1,
        step=1,
    )
    # Channel 2 Voltage
    .add_dpid_integer(
        dpid=20,
        dpcode="cur_voltage2",
        dpmode=DPMode.READ,
        unit="V",
        min=0,
        max=5000,
        scale=1,
        step=1,
    )
    # Channel 2 Total Energy
    .add_dpid_integer(
        dpid=17,
        dpcode="add_ele2",
        dpmode=DPMode.READ,
        unit="kwh",
        min=0,
        max=50000,
        scale=3,
        step=100,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
