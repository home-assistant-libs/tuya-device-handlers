"""Quirk for Tuya EV charger (qccdz) with product_id tj9l3ghsjnbdjom6.

Tested with: Absina Mobile Wallbox 11 kW
https://www.absina.com/products/mobile-wallbox-cee-11kw

The charger reports its status and live measurements on
vendor-specific DPs that are missing from the cloud spec, while the standard
work_state DP is never reported. This quirk maps the vendor DPs to standard
DP codes, and the vendor status values to the standard work_state values.
Writable vendor DPs (e.g. 114 "Set16A", 118 "SetDelayTime", 119
"SetDefineTime") are not mapped: Home Assistant sends commands through the
Tuya cloud's standard instruction set, which rejects vendor-specific codes.
Comments name the vendor code (Tuya developer portal) and the label shown in
the Tuya device logs where known.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="tj9l3ghsjnbdjom6")
    # DP 3 (standard work_state) is advertised but never reported by the
    # device; the actual charging status is sent on vendor DP 101.
    # DP 101: vendor code "DeviceState", shown as "Device State" in Tuya logs.
    .remove_dpid(dpid=3, dpcode="work_state")
    .remove_dpid(dpid=25, dpcode="charge_energy_once")
    # DP 18 (standard switch) is accepted and echoed back by the device, but
    # has no effect on charging, so it is removed to avoid a dead control.
    .remove_dpid(dpid=18, dpcode="switch")
    # DP 14 (standard work_mode) has no effect on charging and no equivalent
    # in the vendor app; the charger cannot read the vehicle's state of charge.
    .remove_dpid(dpid=14, dpcode="work_mode")
    # DP 15 (standard balance_energy) is never reported by the device.
    .remove_dpid(dpid=15, dpcode="balance_energy")
    # DP 16 (standard clear_energy) is rejected as a cloud command; it can
    # only be written as a property, which Home Assistant cannot do.
    .remove_dpid(dpid=16, dpcode="clear_energy")
    .add_dpid_enum(
        dpid=101,
        dpcode="work_state",
        dpmode=DPMode.READ,
        enum_range=[
            "charger_free",
            "charger_insert",
            "charger_wait",
            "charger_charging",
            "charger_end",
            "charger_fault",
        ],
    )
    # DP 101 sends the device's own values (misspellings included); map them
    # to the standard work_state values.
    .set_dpid_strategy_to_enum(
        dpid=101,
        dpcode="work_state",
        enum_mapping_map={
            "no_connet": "charger_free",  # unplugged, "Ready" in the app
            "connect": "charger_insert",  # plugged in, not charging
            "charing": "charger_charging",
            "wait_rfid": "charger_wait",  # waiting for the RFID card
            "wait_charing": "charger_wait",  # delayed start (DP 118)
            "finish": "charger_end",  # charging ended with the RFID card
            "error": "charger_fault",
        },
    )
    # DP 102: voltage, 1 V resolution (raw 415 -> 415 V)
    # Vendor code "A_Voltage", shown as "Voltage" in Tuya logs. The data
    # model labels it phase A, but on this 3-phase charger it reads ~415 V.
    # The per-phase DPs 103/104 (voltage), 106/107 (current) and the
    # PhaseFlag DP 108 are defined in the data model but never reported.
    .add_dpid_integer(
        dpid=102,
        dpcode="cur_voltage",
        dpmode=DPMode.READ,
        unit="V",
        min=0,
        max=500,
        scale=0,
        step=1,
    )
    # DP 105: current, 0.1 A resolution (raw 153 -> 15.3 A)
    # Vendor code "A_Current", shown as "Current" in Tuya logs.
    .add_dpid_integer(
        dpid=105,
        dpcode="cur_current",
        dpmode=DPMode.READ,
        unit="A",
        min=0,
        max=1000,
        scale=1,
        step=1,
    )
    # DP 109: total charging power, 0.1 kW resolution (raw 110 -> 11.0 kW)
    # Verified against the Smart Life app (10.8-11.2 kW).
    # Vendor code "DeviceKw", shown as "Power" in Tuya logs.
    # The portal lists the range as "0 - 1000kW"; raw values are tenths of
    # a kW, as confirmed against the app, hence scale=1.
    .add_dpid_integer(
        dpid=109,
        dpcode="power_total",
        dpmode=DPMode.READ,
        unit="kW",
        min=0,
        max=1000,
        scale=1,
        step=1,
    )
    # DP 110: temperature, 0.1 degC resolution (raw 356 -> 35.6 degC)
    # Vendor code "DeviceTemp", shown as "Temperature" in Tuya logs.
    # The portal lists the raw range as "-300 - 1050"; with scale=1 that is
    # -30.0 to 105.0 degC.
    .add_dpid_integer(
        dpid=110,
        dpcode="temp_current",
        dpmode=DPMode.READ,
        unit="°C",
        min=-300,
        max=1050,
        scale=1,
        step=1,
    )
    # DP 112: energy of the current charging session, 0.1 kWh resolution,
    # reset when the plug is removed. Replaces the standard
    # charge_energy_once DP 25, which the device does not update.
    # Vendor code "DeviceKwh", shown as "Energy" in Tuya logs.
    # The portal lists the raw range as "0 - 10000"; with scale=1 that is
    # 0 to 1000.0 kWh.
    .add_dpid_integer(
        dpid=112,
        dpcode="charge_energy_once",
        dpmode=DPMode.READ,
        unit="kWh",
        min=0,
        max=10000,
        scale=1,
        step=1,
    )
    # DP 121: charging duration, 0.1 h resolution (raw 8 -> 0.8 h)
    # Vendor code "CTime2" (0 - 480 h), shown as "Charging time" in Tuya logs.
    .add_dpid_integer(
        dpid=121,
        dpcode="charge_time",
        dpmode=DPMode.READ,
        unit="h",
        min=0,
        max=480,
        scale=1,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
