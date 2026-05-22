"""Helpers for quirk binary sensor tests.

The category-to-DPCode mapping below mirrors the ``BINARY_SENSORS``
dictionary in Home Assistant core, so tests can assert that a quirk
produces the binary sensors core would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/binary_sensor.py
"""

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.binary_sensor import (
    BinarySensorDefinition,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.common import DPCodeWrapper

_OnValue = bool | float | int | str | set[bool | float | int | str]
# A binary sensor entry is a DPCode, optionally paired with the bitmap key
# and/or "on" value Home Assistant core uses to decode it.
_BinarySensorEntry = str | tuple[str, str | None, _OnValue]

_BINARY_SENSOR_DPCODES: dict[str, tuple[_BinarySensorEntry, ...]] = {
    "co2bj": (
        ("co2_state", None, "alarm"),
        "temper_alarm",
    ),
    "cobj": (
        ("co_state", None, "1"),
        ("co_status", None, "alarm"),
        "temper_alarm",
    ),
    "cs": (
        ("fault", "water_full", True),
        ("fault", "tankfull", True),
        ("fault", "FULL", True),
        ("fault", "defrost", True),
        ("fault", "COIL", True),
        ("fault", "wet", True),
        ("fault", "Cleaning", True),
        ("fault", "E1", True),
        ("fault", "CL", True),
        ("fault", "CH", True),
        ("fault", "LO", True),
        ("fault", "MOTOR", True),
    ),
    "cwwsq": (
        ("feed_state", None, "feeding"),
        "charge_state",
    ),
    "dgnbj": (
        ("gas_sensor_state", None, "alarm"),
        ("ch4_sensor_state", None, "alarm"),
        ("voc_state", None, "alarm"),
        ("pm25_state", None, "alarm"),
        ("co_state", None, "alarm"),
        ("co2_state", None, "alarm"),
        ("ch2o_state", None, "alarm"),
        "doorcontact_state",
        ("watersensor_state", None, "alarm"),
        ("pressure_state", None, "alarm"),
        ("smoke_sensor_state", None, "alarm"),
        "temper_alarm",
    ),
    "hps": (
        (
            "presence_state",
            None,
            {"presence", "small_move", "large_move", "peaceful"},
        ),
    ),
    "jqbj": (
        ("ch2o_state", None, "alarm"),
        "temper_alarm",
    ),
    "jwbj": (
        ("ch4_sensor_state", None, "alarm"),
        "temper_alarm",
    ),
    "ldcg": (
        "temper_alarm",
        "temper_alarm",
    ),
    "mc": (("status", None, {"open", "opened"}),),
    "mcs": (
        "doorcontact_state",
        "switch",
        "temper_alarm",
    ),
    "mk": (("closed_opened_kit", None, {"AQAB"}),),
    "msp": (
        ("fault", "full_fault", True),
        ("fault", "box_out", True),
    ),
    "pir": (
        ("pir", None, "pir"),
        "temper_alarm",
    ),
    "pm2.5": (
        ("pm25_state", None, "alarm"),
        "temper_alarm",
    ),
    "qxj": (),
    "rqbj": (
        ("gas_sensor_status", None, "alarm"),
        ("gas_sensor_state", None, "1"),
        "temper_alarm",
    ),
    "sgbj": (
        "charge_state",
        "temper_alarm",
    ),
    "sj": (
        ("watersensor_state", None, {"1", "alarm"}),
        "temper_alarm",
    ),
    "sos": (
        "sos_state",
        "temper_alarm",
    ),
    "voc": (
        ("voc_state", None, "alarm"),
        "temper_alarm",
    ),
    "wg2": (
        ("master_state", None, "alarm"),
        "charge_state",
    ),
    "wk": (("valve_state", None, "open"),),
    "wkf": (("window_state", None, "opened"),),
    "wsdcg": (),
    "ylcg": (
        ("pressure_state", None, "alarm"),
        "temper_alarm",
    ),
    "ywbj": (
        ("smoke_sensor_status", None, "alarm"),
        ("smoke_sensor_state", None, {"1", "alarm"}),
        "temper_alarm",
    ),
    "zd": (
        ("shock_state", None, "vibration"),
        ("shock_state", None, "drop"),
        ("shock_state", None, "tilt"),
    ),
}


def get_binary_sensor_default_definitions(
    device: CustomerDevice,
) -> list[BinarySensorDefinition]:
    """Get the default binary sensor definitions for a device."""
    values: list[BinarySensorDefinition | None] = []
    for entry in _BINARY_SENSOR_DPCODES.get(device.category, ()):
        if isinstance(entry, str):
            values.append(get_default_definition(device, entry))
        else:
            dpcode, bitmap_key, on_value = entry
            values.append(
                get_default_definition(device, dpcode, bitmap_key, on_value)
            )
    return [definition for definition in values if definition]


def get_binary_sensor_wrapper(
    definitions: list[BinarySensorDefinition], dpcode: str
) -> DPCodeWrapper | None:
    """Extract the binary sensor wrapper for a DPCode from a list."""
    for definition in definitions:
        wrapper = definition.binary_sensor_wrapper
        if isinstance(wrapper, DPCodeWrapper) and wrapper.dpcode == dpcode:
            return wrapper
    return None
