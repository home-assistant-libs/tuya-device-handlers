"""Definitions for climate entity"""

from dataclasses import dataclass

from ..device_wrapper import DeviceWrapper
from ..helpers.homeassistant import (
    TuyaClimateHVACMode,
    TuyaClimateSwingMode,
    TuyaUnitOfTemperature,
)


@dataclass
class ClimateDefinition:
    key: str

    current_humidity_wrapper: DeviceWrapper[int] | None
    current_temperature_wrapper: DeviceWrapper[float] | None
    fan_mode_wrapper: DeviceWrapper[str] | None
    hvac_mode_wrapper: DeviceWrapper[TuyaClimateHVACMode] | None
    preset_wrapper: DeviceWrapper[str] | None
    set_temperature_wrapper: DeviceWrapper[float] | None
    swing_wrapper: DeviceWrapper[TuyaClimateSwingMode] | None
    switch_wrapper: DeviceWrapper[bool] | None
    target_humidity_wrapper: DeviceWrapper[int] | None
    temperature_unit: TuyaUnitOfTemperature
