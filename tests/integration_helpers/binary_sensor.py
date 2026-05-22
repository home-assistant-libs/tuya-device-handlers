"""Helpers for quirk binary sensor tests.

The category mapping below mirrors the ``BINARY_SENSORS`` dictionary in Home
Assistant core, so tests can assert that a quirk produces the binary sensors
core would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/binary_sensor.py
"""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.binary_sensor import (
    BinarySensorDefinition,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.common import DPCodeWrapper

_OnValue = bool | float | int | str | set[bool | float | int | str]


@dataclass(frozen=True)
class BinarySensorEntityDescription:
    """Describes a Tuya binary sensor, mirroring the Home Assistant mapping."""

    dpcode: str
    bitmap_key: str | None = None
    on_value: _OnValue = True


_BINARY_SENSORS: dict[str, tuple[BinarySensorEntityDescription, ...]] = {
    "co2bj": (
        BinarySensorEntityDescription("co2_state", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "cobj": (
        BinarySensorEntityDescription("co_state", on_value="1"),
        BinarySensorEntityDescription("co_status", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "cs": (
        BinarySensorEntityDescription("fault", bitmap_key="water_full"),
        BinarySensorEntityDescription("fault", bitmap_key="tankfull"),
        BinarySensorEntityDescription("fault", bitmap_key="FULL"),
        BinarySensorEntityDescription("fault", bitmap_key="defrost"),
        BinarySensorEntityDescription("fault", bitmap_key="COIL"),
        BinarySensorEntityDescription("fault", bitmap_key="wet"),
        BinarySensorEntityDescription("fault", bitmap_key="Cleaning"),
        BinarySensorEntityDescription("fault", bitmap_key="E1"),
        BinarySensorEntityDescription("fault", bitmap_key="CL"),
        BinarySensorEntityDescription("fault", bitmap_key="CH"),
        BinarySensorEntityDescription("fault", bitmap_key="LO"),
        BinarySensorEntityDescription("fault", bitmap_key="MOTOR"),
    ),
    "cwwsq": (
        BinarySensorEntityDescription("feed_state", on_value="feeding"),
        BinarySensorEntityDescription("charge_state"),
    ),
    "dgnbj": (
        BinarySensorEntityDescription("gas_sensor_state", on_value="alarm"),
        BinarySensorEntityDescription("ch4_sensor_state", on_value="alarm"),
        BinarySensorEntityDescription("voc_state", on_value="alarm"),
        BinarySensorEntityDescription("pm25_state", on_value="alarm"),
        BinarySensorEntityDescription("co_state", on_value="alarm"),
        BinarySensorEntityDescription("co2_state", on_value="alarm"),
        BinarySensorEntityDescription("ch2o_state", on_value="alarm"),
        BinarySensorEntityDescription("doorcontact_state"),
        BinarySensorEntityDescription("watersensor_state", on_value="alarm"),
        BinarySensorEntityDescription("pressure_state", on_value="alarm"),
        BinarySensorEntityDescription("smoke_sensor_state", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "hps": (
        BinarySensorEntityDescription(
            "presence_state",
            on_value={"presence", "small_move", "large_move", "peaceful"},
        ),
    ),
    "jqbj": (
        BinarySensorEntityDescription("ch2o_state", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "jwbj": (
        BinarySensorEntityDescription("ch4_sensor_state", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "ldcg": (
        BinarySensorEntityDescription("temper_alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "mc": (
        BinarySensorEntityDescription("status", on_value={"open", "opened"}),
    ),
    "mcs": (
        BinarySensorEntityDescription("doorcontact_state"),
        BinarySensorEntityDescription("switch"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "mk": (
        BinarySensorEntityDescription("closed_opened_kit", on_value={"AQAB"}),
    ),
    "msp": (
        BinarySensorEntityDescription("fault", bitmap_key="full_fault"),
        BinarySensorEntityDescription("fault", bitmap_key="box_out"),
    ),
    "pir": (
        BinarySensorEntityDescription("pir", on_value="pir"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "pm2.5": (
        BinarySensorEntityDescription("pm25_state", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "qxj": (),
    "rqbj": (
        BinarySensorEntityDescription("gas_sensor_status", on_value="alarm"),
        BinarySensorEntityDescription("gas_sensor_state", on_value="1"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "sgbj": (
        BinarySensorEntityDescription("charge_state"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "sj": (
        BinarySensorEntityDescription(
            "watersensor_state", on_value={"1", "alarm"}
        ),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "sos": (
        BinarySensorEntityDescription("sos_state"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "voc": (
        BinarySensorEntityDescription("voc_state", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "wg2": (
        BinarySensorEntityDescription("master_state", on_value="alarm"),
        BinarySensorEntityDescription("charge_state"),
    ),
    "wk": (BinarySensorEntityDescription("valve_state", on_value="open"),),
    "wkf": (BinarySensorEntityDescription("window_state", on_value="opened"),),
    "wsdcg": (),
    "ylcg": (
        BinarySensorEntityDescription("pressure_state", on_value="alarm"),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "ywbj": (
        BinarySensorEntityDescription("smoke_sensor_status", on_value="alarm"),
        BinarySensorEntityDescription(
            "smoke_sensor_state", on_value={"1", "alarm"}
        ),
        BinarySensorEntityDescription("temper_alarm"),
    ),
    "zd": (
        BinarySensorEntityDescription("shock_state", on_value="vibration"),
        BinarySensorEntityDescription("shock_state", on_value="drop"),
        BinarySensorEntityDescription("shock_state", on_value="tilt"),
    ),
}


def get_binary_sensor_default_definitions(
    device: CustomerDevice,
) -> list[BinarySensorDefinition]:
    """Get the default binary sensor definitions for a device."""
    values = [
        get_default_definition(
            device,
            description.dpcode,
            description.bitmap_key,
            description.on_value,
        )
        for description in _BINARY_SENSORS.get(device.category, ())
    ]
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
