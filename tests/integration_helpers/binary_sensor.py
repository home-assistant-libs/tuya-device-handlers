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

_OnValue = bool | float | int | str | set[bool | float | int | str]


@dataclass(frozen=True)
class BinarySensorEntityDescription:
    """Describes a Tuya binary sensor, mirroring the Home Assistant mapping."""

    key: str
    dpcode: str | None = None
    bitmap_key: str | None = None
    on_value: _OnValue = True


# Tamper binary sensor reused across categories, mirroring Home Assistant core.
TAMPER_BINARY_SENSOR = BinarySensorEntityDescription("temper_alarm")

_BINARY_SENSORS: dict[str, tuple[BinarySensorEntityDescription, ...]] = {
    "co2bj": (
        BinarySensorEntityDescription("co2_state", on_value="alarm"),
        TAMPER_BINARY_SENSOR,
    ),
    "cobj": (
        BinarySensorEntityDescription("co_state", on_value="1"),
        BinarySensorEntityDescription("co_status", on_value="alarm"),
        TAMPER_BINARY_SENSOR,
    ),
    "cs": (
        BinarySensorEntityDescription(
            "fault_water_full", dpcode="fault", bitmap_key="water_full"
        ),
        BinarySensorEntityDescription(
            "tankfull", dpcode="fault", bitmap_key="tankfull"
        ),
        BinarySensorEntityDescription(
            "fault_FULL", dpcode="fault", bitmap_key="FULL"
        ),
        BinarySensorEntityDescription(
            "defrost", dpcode="fault", bitmap_key="defrost"
        ),
        BinarySensorEntityDescription(
            "fault_COIL", dpcode="fault", bitmap_key="COIL"
        ),
        BinarySensorEntityDescription("wet", dpcode="fault", bitmap_key="wet"),
        BinarySensorEntityDescription(
            "fault_Cleaning", dpcode="fault", bitmap_key="Cleaning"
        ),
        BinarySensorEntityDescription(
            "fault_E1", dpcode="fault", bitmap_key="E1"
        ),
        BinarySensorEntityDescription(
            "fault_CL", dpcode="fault", bitmap_key="CL"
        ),
        BinarySensorEntityDescription(
            "fault_CH", dpcode="fault", bitmap_key="CH"
        ),
        BinarySensorEntityDescription(
            "fault_LO", dpcode="fault", bitmap_key="LO"
        ),
        BinarySensorEntityDescription(
            "fault_MOTOR", dpcode="fault", bitmap_key="MOTOR"
        ),
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
        TAMPER_BINARY_SENSOR,
    ),
    "hps": (
        BinarySensorEntityDescription(
            "presence_state",
            on_value={"presence", "small_move", "large_move", "peaceful"},
        ),
    ),
    "jqbj": (
        BinarySensorEntityDescription("ch2o_state", on_value="alarm"),
        TAMPER_BINARY_SENSOR,
    ),
    "jwbj": (
        BinarySensorEntityDescription("ch4_sensor_state", on_value="alarm"),
        TAMPER_BINARY_SENSOR,
    ),
    "ldcg": (TAMPER_BINARY_SENSOR,),
    "mc": (
        BinarySensorEntityDescription("status", on_value={"open", "opened"}),
    ),
    "mcs": (
        BinarySensorEntityDescription("doorcontact_state"),
        BinarySensorEntityDescription("switch"),
        TAMPER_BINARY_SENSOR,
    ),
    "mk": (
        BinarySensorEntityDescription("closed_opened_kit", on_value={"AQAB"}),
    ),
    "msp": (
        BinarySensorEntityDescription(
            "fault_full_fault", dpcode="fault", bitmap_key="full_fault"
        ),
        BinarySensorEntityDescription(
            "fault_box_out", dpcode="fault", bitmap_key="box_out"
        ),
    ),
    "pir": (
        BinarySensorEntityDescription("pir", on_value="pir"),
        TAMPER_BINARY_SENSOR,
    ),
    "pm2.5": (
        BinarySensorEntityDescription("pm25_state", on_value="alarm"),
        TAMPER_BINARY_SENSOR,
    ),
    "qxj": (),
    "rqbj": (
        BinarySensorEntityDescription("gas_sensor_status", on_value="alarm"),
        BinarySensorEntityDescription("gas_sensor_state", on_value="1"),
        TAMPER_BINARY_SENSOR,
    ),
    "sgbj": (
        BinarySensorEntityDescription("charge_state"),
        TAMPER_BINARY_SENSOR,
    ),
    "sj": (
        BinarySensorEntityDescription(
            "watersensor_state", on_value={"1", "alarm"}
        ),
        TAMPER_BINARY_SENSOR,
    ),
    "sos": (
        BinarySensorEntityDescription("sos_state"),
        TAMPER_BINARY_SENSOR,
    ),
    "voc": (
        BinarySensorEntityDescription("voc_state", on_value="alarm"),
        TAMPER_BINARY_SENSOR,
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
        TAMPER_BINARY_SENSOR,
    ),
    "ywbj": (
        BinarySensorEntityDescription("smoke_sensor_status", on_value="alarm"),
        BinarySensorEntityDescription(
            "smoke_sensor_state", on_value={"1", "alarm"}
        ),
        TAMPER_BINARY_SENSOR,
    ),
    "zd": (
        BinarySensorEntityDescription(
            "shock_state_vibration", dpcode="shock_state", on_value="vibration"
        ),
        BinarySensorEntityDescription(
            "shock_state_drop", dpcode="shock_state", on_value="drop"
        ),
        BinarySensorEntityDescription(
            "shock_state_tilt", dpcode="shock_state", on_value="tilt"
        ),
    ),
}


def get_binary_sensor_default_definitions(
    device: CustomerDevice,
) -> dict[str, BinarySensorDefinition]:
    """Get the default binary sensor definitions for a device."""
    return {
        description.key: definition
        for description in _BINARY_SENSORS.get(device.category, ())
        if (
            definition := get_default_definition(
                device,
                description.dpcode or description.key,
                description.bitmap_key,
                description.on_value,
            )
        )
    }
