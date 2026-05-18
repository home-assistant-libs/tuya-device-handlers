"""Quirk for Quark inverter pool heat pump (product_id 5xe6dkfmdafvrasa).

OEM-branded as Madimack Elite V4-120 in Australia among others. Tuya cloud
returns empty ``function``/``status_range``/``local_strategy`` for this
device, so Home Assistant cannot build a usable climate entity. The
datapoint definitions below were retrieved from the Tuya Developer Portal
Standard Instruction Set for product ``5xe6dkfmdafvrasa`` (夸克热泵20231219 /
"Quark heat pump 20231219").

DP 117 (``temp_inflow``) and DP 114 (``temp_effluent``) report water
temperatures multiplied by 10 (i.e. 305 means 30.5 °C); all other temperature
DPs are reported as whole °C.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="5xe6dkfmdafvrasa")
    # Power on/off.
    .add_dpid_boolean(
        dpid=101,
        dpcode="switch1",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    # Operating mode.
    .add_dpid_enum(
        dpid=102,
        dpcode="mode1",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["heating", "cooling", "auto"],
    )
    # Child lock.
    .add_dpid_boolean(
        dpid=103,
        dpcode="child_lock1",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    # Target water temperature.
    .add_dpid_integer(
        dpid=104,
        dpcode="temp_set1",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℃",
        min=7,
        max=35,
        scale=0,
        step=1,
    )
    # Work mode preset (turbo / silent / smart).
    .add_dpid_enum(
        dpid=105,
        dpcode="work_mode",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["power", "silent", "smart"],
    )
    # Temperature unit (celsius / fahrenheit).
    .add_dpid_enum(
        dpid=106,
        dpcode="temp_unit_convert1",
        dpmode=DPMode.READ | DPMode.WRITE,
        enum_range=["c", "f"],
    )
    # Fault code (primary).
    .add_dpid_integer(
        dpid=107,
        dpcode="fault1",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=255,
        scale=0,
        step=1,
    )
    # Current temperature (display-side, mirrors inflow).
    .add_dpid_integer(
        dpid=108,
        dpcode="temp_current1",
        dpmode=DPMode.READ,
        unit="℃",
        min=-30,
        max=99,
        scale=0,
        step=1,
    )
    # Compressor speed / load.
    .add_dpid_integer(
        dpid=109,
        dpcode="compressor_strength",
        dpmode=DPMode.READ,
        unit="%",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    # User-configurable upper temperature limit.
    .add_dpid_integer(
        dpid=110,
        dpcode="temp_top",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℃",
        min=7,
        max=45,
        scale=0,
        step=1,
    )
    # User-configurable lower temperature limit.
    .add_dpid_integer(
        dpid=111,
        dpcode="temp_bottom",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="℃",
        min=-30,
        max=35,
        scale=0,
        step=1,
    )
    # Outer coil temperature.
    .add_dpid_integer(
        dpid=112,
        dpcode="temp_coiler",
        dpmode=DPMode.READ,
        unit="℃",
        min=-30,
        max=99,
        scale=0,
        step=1,
    )
    # Compressor discharge temperature.
    .add_dpid_integer(
        dpid=113,
        dpcode="temp_venting",
        dpmode=DPMode.READ,
        unit="℃",
        min=-30,
        max=150,
        scale=0,
        step=1,
    )
    # Effluent (outlet) water temperature, reported x10.
    .add_dpid_integer(
        dpid=114,
        dpcode="temp_effluent",
        dpmode=DPMode.READ,
        unit="℃",
        min=-300,
        max=990,
        scale=1,
        step=1,
    )
    # Ambient air temperature.
    .add_dpid_integer(
        dpid=115,
        dpcode="temp_around",
        dpmode=DPMode.READ,
        unit="℃",
        min=-50,
        max=99,
        scale=0,
        step=1,
    )
    # Fault code (secondary).
    .add_dpid_integer(
        dpid=116,
        dpcode="fault2",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=255,
        scale=0,
        step=1,
    )
    # Inflow (inlet) water temperature, reported x10.
    .add_dpid_integer(
        dpid=117,
        dpcode="temp_inflow",
        dpmode=DPMode.READ,
        unit="℃",
        min=-300,
        max=990,
        scale=1,
        step=1,
    )
    # Refrigerant return-line temperature.
    .add_dpid_integer(
        dpid=118,
        dpcode="temp_return",
        dpmode=DPMode.READ,
        unit="℃",
        min=-30,
        max=99,
        scale=0,
        step=1,
    )
    # Inner coil temperature.
    .add_dpid_integer(
        dpid=119,
        dpcode="temp_coiler_inside",
        dpmode=DPMode.READ,
        unit="℃",
        min=-30,
        max=99,
        scale=0,
        step=1,
    )
    # Radiator/heat-exchanger temperature.
    .add_dpid_integer(
        dpid=120,
        dpcode="temp_radiator",
        dpmode=DPMode.READ,
        unit="℃",
        min=-30,
        max=99,
        scale=0,
        step=1,
    )
    # Electronic expansion valve opening (steps).
    .add_dpid_integer(
        dpid=121,
        dpcode="expansion_valve",
        dpmode=DPMode.READ,
        unit="",
        min=0,
        max=1000,
        scale=0,
        step=1,
    )
    # Power-monitoring active flag (semantics inferred).
    .add_dpid_boolean(
        dpid=122,
        dpcode="power_w",
        dpmode=DPMode.READ,
    )
    # Cool-mode enable interlock.
    .add_dpid_boolean(
        dpid=123,
        dpcode="cool_enable",
        dpmode=DPMode.READ | DPMode.WRITE,
    )
    # Operating cycle indicator (defrost / heating / standby etc.).
    .add_dpid_enum(
        dpid=124,
        dpcode="oc_mode",
        dpmode=DPMode.READ,
        enum_range=["oc_1", "oc_2", "oc_3", "oc_4", "oc_5"],
    )
    # Instantaneous power consumption (W).
    .add_dpid_integer(
        dpid=125,
        dpcode="power",
        dpmode=DPMode.READ,
        unit="W",
        min=0,
        max=10000,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
