"""Helpers for quirk sensor tests.

The category mapping below mirrors the ``SENSORS`` dictionary in Home
Assistant core, so tests can assert that a quirk produces the sensors core
would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/sensor.py
"""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.sensor import (
    SensorDefinition,
    get_default_definition,
)
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.sensor import (
    ElectricityCurrentJsonWrapper,
    ElectricityCurrentRawWrapper,
    ElectricityPowerJsonWrapper,
    ElectricityPowerRawWrapper,
    ElectricityVoltageJsonWrapper,
    ElectricityVoltageRawWrapper,
    WindDirectionEnumWrapper,
)

_WrapperClasses = tuple[type[DPCodeTypeInformationWrapper], ...]

# Wrapper tuples for RAW/JSON electricity DPs, mirroring Home Assistant core.
_CURRENT_WRAPPER = (ElectricityCurrentRawWrapper, ElectricityCurrentJsonWrapper)
_POWER_WRAPPER = (ElectricityPowerRawWrapper, ElectricityPowerJsonWrapper)
_VOLTAGE_WRAPPER = (ElectricityVoltageRawWrapper, ElectricityVoltageJsonWrapper)
_WIND_DIRECTION_WRAPPER = (WindDirectionEnumWrapper,)


@dataclass(frozen=True)
class SensorEntityDescription:
    """Describes a Tuya sensor, mirroring the Home Assistant core mapping."""

    key: str
    dpcode: str | None = None
    wrapper_class: _WrapperClasses | None = None


# Battery sensors reused across categories, mirroring Home Assistant core.
BATTERY_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription("battery_percentage"),
    SensorEntityDescription("battery"),
    SensorEntityDescription("battery_state"),
    SensorEntityDescription("battery_value"),
    SensorEntityDescription("va_battery"),
)

_SENSORS: dict[str, tuple[SensorEntityDescription, ...]] = {
    "aqcz": (
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
    ),
    "bh": (
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("temp_current_f"),
        SensorEntityDescription("status"),
    ),
    "cl": (SensorEntityDescription("time_total"),),
    "co2bj": (
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("co2_value"),
        SensorEntityDescription("ch2o_value"),
        SensorEntityDescription("voc_value"),
        SensorEntityDescription("pm25_value"),
        SensorEntityDescription("pm10"),
        *BATTERY_SENSORS,
    ),
    "cobj": (
        SensorEntityDescription("co_value"),
        *BATTERY_SENSORS,
    ),
    "cs": (
        SensorEntityDescription("temp_indoor"),
        SensorEntityDescription("humidity_indoor"),
    ),
    "cwjwq": (
        SensorEntityDescription("work_state_e"),
        *BATTERY_SENSORS,
    ),
    "cwwsq": (
        *BATTERY_SENSORS,
        SensorEntityDescription("feed_report"),
    ),
    "cwysj": (
        SensorEntityDescription("uv_runtime"),
        SensorEntityDescription("pump_time"),
        SensorEntityDescription("filter_life"),
        SensorEntityDescription("water_time"),
        SensorEntityDescription("water_level"),
    ),
    "cz": (
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
        SensorEntityDescription("add_ele"),
        SensorEntityDescription("pro_add_ele"),
    ),
    "dghsxj": (
        SensorEntityDescription("sensor_temperature"),
        SensorEntityDescription("sensor_humidity"),
        SensorEntityDescription("wireless_electricity"),
    ),
    "dgnbj": (
        SensorEntityDescription("gas_sensor_value"),
        SensorEntityDescription("ch4_sensor_value"),
        SensorEntityDescription("voc_value"),
        SensorEntityDescription("pm25_value"),
        SensorEntityDescription("co_value"),
        SensorEntityDescription("co2_value"),
        SensorEntityDescription("ec_current"),
        SensorEntityDescription("ch2o_value"),
        SensorEntityDescription("bright_state"),
        SensorEntityDescription("bright_value"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("orp_current"),
        SensorEntityDescription("ph_current"),
        SensorEntityDescription("smoke_sensor_value"),
        *BATTERY_SENSORS,
    ),
    "dlq": (
        SensorEntityDescription("total_forward_energy"),
        SensorEntityDescription("add_ele"),
        SensorEntityDescription("forward_energy_total"),
        SensorEntityDescription("reverse_energy_total"),
        SensorEntityDescription("cur_neutral"),
        SensorEntityDescription("supply_frequency"),
        SensorEntityDescription(
            "phase_aelectriccurrent",
            dpcode="phase_a",
            wrapper_class=_CURRENT_WRAPPER,
        ),
        SensorEntityDescription(
            "phase_apower", dpcode="phase_a", wrapper_class=_POWER_WRAPPER
        ),
        SensorEntityDescription(
            "phase_avoltage", dpcode="phase_a", wrapper_class=_VOLTAGE_WRAPPER
        ),
        SensorEntityDescription(
            "phase_belectriccurrent",
            dpcode="phase_b",
            wrapper_class=_CURRENT_WRAPPER,
        ),
        SensorEntityDescription(
            "phase_bpower", dpcode="phase_b", wrapper_class=_POWER_WRAPPER
        ),
        SensorEntityDescription(
            "phase_bvoltage", dpcode="phase_b", wrapper_class=_VOLTAGE_WRAPPER
        ),
        SensorEntityDescription(
            "phase_celectriccurrent",
            dpcode="phase_c",
            wrapper_class=_CURRENT_WRAPPER,
        ),
        SensorEntityDescription(
            "phase_cpower", dpcode="phase_c", wrapper_class=_POWER_WRAPPER
        ),
        SensorEntityDescription(
            "phase_cvoltage", dpcode="phase_c", wrapper_class=_VOLTAGE_WRAPPER
        ),
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
    ),
    "fs": (SensorEntityDescription("temp_current"),),
    "ggq": (*BATTERY_SENSORS,),
    "hjjcy": (
        SensorEntityDescription("air_quality_index"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("co2_value"),
        SensorEntityDescription("ch2o_value"),
        SensorEntityDescription("voc_value"),
        SensorEntityDescription("pm25_value"),
        SensorEntityDescription("pm10"),
        *BATTERY_SENSORS,
    ),
    "jqbj": (
        SensorEntityDescription("co2_value"),
        SensorEntityDescription("voc_value"),
        SensorEntityDescription("pm25_value"),
        SensorEntityDescription("va_humidity"),
        SensorEntityDescription("va_temperature"),
        SensorEntityDescription("ch2o_value"),
        *BATTERY_SENSORS,
    ),
    "jsq": (
        SensorEntityDescription("humidity_current"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("temp_current_f"),
        SensorEntityDescription("level_current"),
    ),
    "jwbj": (
        SensorEntityDescription("ch4_sensor_value"),
        *BATTERY_SENSORS,
    ),
    "kg": (
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
        SensorEntityDescription("add_ele"),
        SensorEntityDescription("pro_add_ele"),
    ),
    "kj": (
        SensorEntityDescription("filter"),
        SensorEntityDescription("pm25"),
        SensorEntityDescription("temp"),
        SensorEntityDescription("humidity"),
        SensorEntityDescription("tvoc"),
        SensorEntityDescription("eco2"),
        SensorEntityDescription("total_time"),
        SensorEntityDescription("total_pm"),
        SensorEntityDescription("air_quality"),
    ),
    "ldcg": (
        SensorEntityDescription("bright_state"),
        SensorEntityDescription("bright_value"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("co2_value"),
        *BATTERY_SENSORS,
    ),
    "mc": (*BATTERY_SENSORS,),
    "mcs": (*BATTERY_SENSORS,),
    "msp": (
        SensorEntityDescription("cat_weight"),
        SensorEntityDescription("excretion_time_day"),
        SensorEntityDescription("excretion_times_day"),
        SensorEntityDescription("status"),
    ),
    "mzj": (
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("status"),
        SensorEntityDescription("remain_time"),
    ),
    "pc": (
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
        SensorEntityDescription("add_ele"),
        SensorEntityDescription("pro_add_ele"),
    ),
    "pir": (*BATTERY_SENSORS,),
    "pm2.5": (
        SensorEntityDescription("pm25_value"),
        SensorEntityDescription("ch2o_value"),
        SensorEntityDescription("voc_value"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("co2_value"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("pm1"),
        SensorEntityDescription("pm10"),
        *BATTERY_SENSORS,
    ),
    "qn": (SensorEntityDescription("work_power"),),
    "qxj": (
        SensorEntityDescription("va_temperature"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("temp_current_external"),
        SensorEntityDescription("temp_current_external_1"),
        SensorEntityDescription("temp_current_external_2"),
        SensorEntityDescription("temp_current_external_3"),
        SensorEntityDescription("va_humidity"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("humidity_outdoor"),
        SensorEntityDescription("humidity_outdoor_1"),
        SensorEntityDescription("humidity_outdoor_2"),
        SensorEntityDescription("humidity_outdoor_3"),
        SensorEntityDescription("atmospheric_pressture"),
        SensorEntityDescription("bright_value"),
        SensorEntityDescription("windspeed_avg"),
        SensorEntityDescription("rain_24h"),
        SensorEntityDescription("rain_rate"),
        SensorEntityDescription("uv_index"),
        SensorEntityDescription(
            "wind_direct", wrapper_class=_WIND_DIRECTION_WRAPPER
        ),
        SensorEntityDescription("dew_point_temp"),
        SensorEntityDescription("feellike_temp"),
        SensorEntityDescription("heat_index"),
        SensorEntityDescription("windchill_index"),
        *BATTERY_SENSORS,
    ),
    "rqbj": (
        SensorEntityDescription("gas_sensor_value"),
        *BATTERY_SENSORS,
    ),
    "sd": (
        SensorEntityDescription("clean_area"),
        SensorEntityDescription("clean_time"),
        SensorEntityDescription("total_clean_area"),
        SensorEntityDescription("total_clean_time"),
        SensorEntityDescription("total_clean_count"),
        SensorEntityDescription("duster_cloth"),
        SensorEntityDescription("edge_brush"),
        SensorEntityDescription("filter"),
        SensorEntityDescription("roll_brush"),
        SensorEntityDescription("electricity_left"),
    ),
    "sfkzq": (
        SensorEntityDescription("time_use"),
        SensorEntityDescription("use_time_one"),
        SensorEntityDescription("work_state"),
        *BATTERY_SENSORS,
    ),
    "sgbj": (*BATTERY_SENSORS,),
    "sj": (*BATTERY_SENSORS,),
    "sos": (*BATTERY_SENSORS,),
    "sp": (
        SensorEntityDescription("sensor_temperature"),
        SensorEntityDescription("sensor_humidity"),
        SensorEntityDescription("wireless_electricity"),
    ),
    "swtz": (
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("temp_current_2"),
        *BATTERY_SENSORS,
    ),
    "sz": (
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("humidity_current"),
    ),
    "szjcy": (
        SensorEntityDescription("tds_in"),
        SensorEntityDescription("temp_current"),
        *BATTERY_SENSORS,
    ),
    "szjqr": (*BATTERY_SENSORS,),
    "tdq": (
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
        SensorEntityDescription("add_ele"),
        SensorEntityDescription("va_temperature"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("va_humidity"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("bright_value"),
        *BATTERY_SENSORS,
    ),
    "tyndj": (*BATTERY_SENSORS,),
    "voc": (
        SensorEntityDescription("co2_value"),
        SensorEntityDescription("pm25_value"),
        SensorEntityDescription("ch2o_value"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("voc_value"),
        *BATTERY_SENSORS,
    ),
    "wg2": (*BATTERY_SENSORS,),
    "wk": (*BATTERY_SENSORS,),
    "wkcz": (
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
    ),
    "wkf": (*BATTERY_SENSORS,),
    "wnykq": (
        SensorEntityDescription("va_temperature"),
        SensorEntityDescription("va_humidity"),
        SensorEntityDescription("cur_current"),
        SensorEntityDescription("cur_power"),
        SensorEntityDescription("cur_voltage"),
    ),
    "wsdcg": (
        SensorEntityDescription("va_temperature"),
        SensorEntityDescription("ext_temp"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("va_humidity"),
        SensorEntityDescription("humidity_value"),
        SensorEntityDescription("bright_value"),
        *BATTERY_SENSORS,
    ),
    "wxkg": (*BATTERY_SENSORS,),
    "xnyjcn": (
        SensorEntityDescription("current_soc"),
        SensorEntityDescription("pv_power_total"),
        SensorEntityDescription("pv_power_channel_1"),
        SensorEntityDescription("pv_power_channel_2"),
        SensorEntityDescription("battery_power"),
        SensorEntityDescription("inverter_output_power"),
        SensorEntityDescription("cumulative_energy_generated_pv"),
        SensorEntityDescription("cumulative_energy_output_inv"),
        SensorEntityDescription("cumulative_energy_discharged"),
        SensorEntityDescription("cumulative_energy_charged"),
        SensorEntityDescription("cuml_e_export_offgrid1"),
    ),
    "ylcg": (
        SensorEntityDescription("pressure_value"),
        *BATTERY_SENSORS,
    ),
    "ywbj": (
        SensorEntityDescription("smoke_sensor_value"),
        *BATTERY_SENSORS,
    ),
    "ywcgq": (
        SensorEntityDescription("liquid_state"),
        SensorEntityDescription("liquid_depth"),
        SensorEntityDescription("liquid_level_percent"),
    ),
    "zd": (*BATTERY_SENSORS,),
    "zndb": (
        SensorEntityDescription("forward_energy_total"),
        SensorEntityDescription("reverse_energy_total"),
        SensorEntityDescription("power_total"),
        SensorEntityDescription("total_powerpower", dpcode="total_power"),
        SensorEntityDescription("supply_frequency"),
        SensorEntityDescription(
            "phase_aelectriccurrent",
            dpcode="phase_a",
            wrapper_class=_CURRENT_WRAPPER,
        ),
        SensorEntityDescription(
            "phase_apower", dpcode="phase_a", wrapper_class=_POWER_WRAPPER
        ),
        SensorEntityDescription(
            "phase_avoltage", dpcode="phase_a", wrapper_class=_VOLTAGE_WRAPPER
        ),
        SensorEntityDescription(
            "phase_belectriccurrent",
            dpcode="phase_b",
            wrapper_class=_CURRENT_WRAPPER,
        ),
        SensorEntityDescription(
            "phase_bpower", dpcode="phase_b", wrapper_class=_POWER_WRAPPER
        ),
        SensorEntityDescription(
            "phase_bvoltage", dpcode="phase_b", wrapper_class=_VOLTAGE_WRAPPER
        ),
        SensorEntityDescription(
            "phase_celectriccurrent",
            dpcode="phase_c",
            wrapper_class=_CURRENT_WRAPPER,
        ),
        SensorEntityDescription(
            "phase_cpower", dpcode="phase_c", wrapper_class=_POWER_WRAPPER
        ),
        SensorEntityDescription(
            "phase_cvoltage", dpcode="phase_c", wrapper_class=_VOLTAGE_WRAPPER
        ),
    ),
    "znnbq": (
        SensorEntityDescription("reverse_energy_total"),
        SensorEntityDescription("power_total"),
        SensorEntityDescription("temp_current"),
    ),
    "znrb": (
        SensorEntityDescription("compressor_strength"),
        SensorEntityDescription("temp_around"),
        SensorEntityDescription("temp_coiler"),
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("temp_effluent"),
        SensorEntityDescription("temp_venting"),
    ),
    "zwjcy": (
        SensorEntityDescription("temp_current"),
        SensorEntityDescription("humidity"),
        *BATTERY_SENSORS,
    ),
}


def get_sensor_default_definitions(
    device: CustomerDevice,
) -> dict[str, SensorDefinition]:
    """Get the default sensor definitions Home Assistant builds for a device."""
    return {
        description.key: definition
        for description in _SENSORS.get(device.category, ())
        if (
            definition := get_default_definition(
                device,
                description.dpcode or description.key,
                description.wrapper_class,
            )
        )
    }
