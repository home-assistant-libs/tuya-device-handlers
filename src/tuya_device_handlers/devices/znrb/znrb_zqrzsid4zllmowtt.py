"""Quirk for TURBRO Beluga B58V pool heat pump (product_id zqrzsid4zllmowtt).

The cloud database under-declares this device's datapoints:

- ``mode`` only lists ``auto``, but the device also reports ``make_hot``
  (and presumably ``make_cold`` in cooling, unconfirmed), which are
  rejected as invalid ENUM values.
- ``work_mode`` (ECO / Normal / Boost) is not declared at all.
- ``temp_current`` (dpid 16) reports the EEV valve opening in pulses
  (unit ``P``), not a temperature; it is removed so Home Assistant does
  not show it as a temperature sensor.
- ``around_temp``, ``coiler_temp``, ``venting_temp`` and ``effluent_temp``
  (dpids 23-26) are reported by the device but not declared; they are
  added under the datapoint codes Home Assistant Core already exposes
  as ``znrb`` temperature sensors.
- ``temp_set`` accepts values down to 47°F in the cloud metadata, but
  the device refuses anything below 59°F, so the minimum is raised.

Upstream issue: https://github.com/home-assistant-libs/tuya-device-handlers/issues/663
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="zqrzsid4zllmowtt")
    .add_dpid_enum(
        dpid=2,
        dpcode="mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["auto", "make_hot", "make_cold"],
    )
    .add_dpid_integer(
        dpid=4,
        dpcode="temp_set",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℉",
        min=59,
        max=104,
        scale=0,
        step=1,
    )
    .add_dpid_enum(
        dpid=5,
        dpcode="work_mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["ECO", "Normal", "Boost"],
    )
    .remove_dpid(dpid=16, dpcode="temp_current")
    .add_dpid_integer(
        dpid=23,
        dpcode="temp_coiler",
        dpmode=DPMode.READ,
        unit="℉",
        min=-1000,
        max=1000,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=24,
        dpcode="temp_venting",
        dpmode=DPMode.READ,
        unit="℉",
        min=-1000,
        max=1000,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=25,
        dpcode="temp_effluent",
        dpmode=DPMode.READ,
        unit="℉",
        min=-1000,
        max=1000,
        scale=0,
        step=1,
    )
    .add_dpid_integer(
        dpid=26,
        dpcode="temp_around",
        dpmode=DPMode.READ,
        unit="℉",
        min=-1000,
        max=1000,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
