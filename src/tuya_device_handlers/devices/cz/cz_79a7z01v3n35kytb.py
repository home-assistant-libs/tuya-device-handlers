"""Tuya Double Digital Meter (79a7z01v3n35kytb) quirk.

Verified against four physical meters on Home Assistant 2026.11.0.
Source: https://github.com/home-assistant-libs/tuya-device-handlers/pull/470
"""
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

q = DeviceQuirk().applies_to(product_id="79a7z01v3n35kytb")
q = q.add_dpid_enum(dpid=103, dpcode="device_state1", dpmode=DPMode.READ, enum_range=["close", "monitor", "working", "warning"])
q = q.add_dpid_enum(dpid=113, dpcode="device_state2", dpmode=DPMode.READ, enum_range=["idle", "monitor", "working", "warning"])
q = q.add_dpid_integer(dpid=105, dpcode="cur_power1", dpmode=DPMode.READ, unit="W", min=0, max=2000000, scale=1, step=1)
q = q.add_dpid_integer(dpid=106, dpcode="cur_current1", dpmode=DPMode.READ, unit="A", min=0, max=800000, scale=3, step=1)
q = q.add_dpid_integer(dpid=107, dpcode="cur_voltage1", dpmode=DPMode.READ, unit="V", min=0, max=5000, scale=1, step=1)
q = q.add_dpid_integer(dpid=108, dpcode="total_energy1", dpmode=DPMode.READ, unit="kWh", min=0, max=2147483647, scale=3, step=1)
q = q.add_dpid_integer(dpid=109, dpcode="today_acc_energy1", dpmode=DPMode.READ, unit="kWh", min=0, max=2147483647, scale=3, step=1)
q = q.add_dpid_integer(dpid=111, dpcode="warn_power1", dpmode=DPMode.READ | DPMode.WRITE, unit="W", min=200, max=50000, scale=0, step=100)
q = q.add_dpid_integer(dpid=115, dpcode="cur_power2", dpmode=DPMode.READ, unit="W", min=0, max=2000000, scale=1, step=1)
q = q.add_dpid_integer(dpid=116, dpcode="cur_current2", dpmode=DPMode.READ, unit="A", min=0, max=800000, scale=3, step=1)
q = q.add_dpid_integer(dpid=117, dpcode="cur_voltage2", dpmode=DPMode.READ, unit="V", min=0, max=5000, scale=1, step=1)
q = q.add_dpid_integer(dpid=118, dpcode="total_energy2", dpmode=DPMode.READ, unit="kWh", min=0, max=2147483647, scale=3, step=1)
q = q.add_dpid_integer(dpid=119, dpcode="today_acc_energy2", dpmode=DPMode.READ, unit="kWh", min=0, max=2147483647, scale=3, step=1)
q = q.add_dpid_integer(dpid=121, dpcode="warn_power2", dpmode=DPMode.READ | DPMode.WRITE, unit="W", min=200, max=50000, scale=0, step=100)
q = q.add_dpid_integer(dpid=123, dpcode="all_energy", dpmode=DPMode.READ, unit="kWh", min=0, max=2147483647, scale=3, step=1)
q.register(TUYA_QUIRKS_REGISTRY)
