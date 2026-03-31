"""Tuya climate definition."""

from collections.abc import Callable
from dataclasses import dataclass

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..const import CELSIUS_ALIASES, FAHRENHEIT_ALIASES
from ..device_wrapper import DeviceWrapper
from ..device_wrapper.climate import (
    DefaultHVACModeWrapper,
    DefaultPresetModeWrapper,
    SwingModeCompositeWrapper,
)
from ..device_wrapper.common import (
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
)
from ..device_wrapper.extended import DPCodeRoundedIntegerWrapper
from ..helpers.homeassistant import (
    TuyaClimateHVACMode,
    TuyaClimateSwingMode,
    TuyaUnitOfTemperature,
)
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class ClimateDefinition:
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


# Deprecated alias for backward compatibility
TuyaClimateDefinition = ClimateDefinition


@dataclass(kw_only=True)
class ClimateQuirk(BaseEntityQuirk):
    """Quirk for a climate entity."""

    definition_fn: Callable[
        [CustomerDevice, TuyaUnitOfTemperature],
        ClimateDefinition | None,
    ]


def _get_temperature_wrapper(
    wrappers: list[DPCodeIntegerWrapper | None], aliases: set[str]
) -> DPCodeIntegerWrapper | None:
    """Return first wrapper with matching unit."""
    return next(
        (
            wrapper
            for wrapper in wrappers
            if wrapper is not None
            and (unit := wrapper.type_information.unit)
            and unit.lower() in aliases
        ),
        None,
    )


def _get_temperature_wrappers(
    device: CustomerDevice, system_temperature_unit: TuyaUnitOfTemperature
) -> tuple[
    DPCodeIntegerWrapper | None,
    DPCodeIntegerWrapper | None,
    TuyaUnitOfTemperature,
]:
    """Get temperature wrappers for current and set temperatures."""
    # Get all possible temperature dpcodes
    temp_current = DPCodeIntegerWrapper.find_dpcode(
        device, ("temp_current", "upper_temp")
    )
    temp_current_f = DPCodeIntegerWrapper.find_dpcode(
        device, ("temp_current_f", "upper_temp_f")
    )
    temp_set = DPCodeIntegerWrapper.find_dpcode(
        device, "temp_set", prefer_function=True
    )
    temp_set_f = DPCodeIntegerWrapper.find_dpcode(
        device, "temp_set_f", prefer_function=True
    )

    # If there is a temp unit convert dpcode, override empty units
    if (
        temp_unit_convert := DPCodeEnumWrapper.find_dpcode(
            device, "temp_unit_convert"
        )
    ) is not None:
        for wrapper in (temp_current, temp_current_f, temp_set, temp_set_f):
            if wrapper is not None and not wrapper.type_information.unit:
                wrapper.type_information.unit = (
                    temp_unit_convert.read_device_status(device)
                )

    # Get wrappers for celsius and fahrenheit
    # We need to check the unit of measurement
    current_celsius = _get_temperature_wrapper(
        [temp_current, temp_current_f], CELSIUS_ALIASES
    )
    current_fahrenheit = _get_temperature_wrapper(
        [temp_current_f, temp_current], FAHRENHEIT_ALIASES
    )
    set_celsius = _get_temperature_wrapper(
        [temp_set, temp_set_f], CELSIUS_ALIASES
    )
    set_fahrenheit = _get_temperature_wrapper(
        [temp_set_f, temp_set], FAHRENHEIT_ALIASES
    )

    # Return early if we have the right wrappers for the system unit
    if system_temperature_unit == TuyaUnitOfTemperature.FAHRENHEIT:
        if (
            (current_fahrenheit and set_fahrenheit)
            or (current_fahrenheit and not set_celsius)
            or (set_fahrenheit and not current_celsius)
        ):
            return (
                current_fahrenheit,
                set_fahrenheit,
                TuyaUnitOfTemperature.FAHRENHEIT,
            )
    if (
        (current_celsius and set_celsius)
        or (current_celsius and not set_fahrenheit)
        or (set_celsius and not current_fahrenheit)
    ):
        return current_celsius, set_celsius, TuyaUnitOfTemperature.CELSIUS

    # If we don't have the right wrappers, return whatever is available
    # and assume system unit
    if system_temperature_unit == TuyaUnitOfTemperature.FAHRENHEIT:
        return (
            temp_current_f or temp_current,
            temp_set_f or temp_set,
            TuyaUnitOfTemperature.FAHRENHEIT,
        )

    return (
        temp_current or temp_current_f,
        temp_set or temp_set_f,
        TuyaUnitOfTemperature.CELSIUS,
    )


def get_default_definition(
    device: CustomerDevice, system_temperature_unit: TuyaUnitOfTemperature
) -> ClimateDefinition:
    temperature_wrappers = _get_temperature_wrappers(
        device, system_temperature_unit
    )
    return ClimateDefinition(
        current_humidity_wrapper=DPCodeRoundedIntegerWrapper.find_dpcode(
            device, "humidity_current"
        ),
        current_temperature_wrapper=temperature_wrappers[0],
        fan_mode_wrapper=DPCodeEnumWrapper.find_dpcode(
            device,
            ("fan_speed_enum", "level", "windspeed"),
            prefer_function=True,
        ),
        hvac_mode_wrapper=DefaultHVACModeWrapper.find_dpcode(
            device, "mode", prefer_function=True
        ),
        preset_wrapper=DefaultPresetModeWrapper.find_dpcode(
            device, "mode", prefer_function=True
        ),
        set_temperature_wrapper=temperature_wrappers[1],
        swing_wrapper=SwingModeCompositeWrapper.find_dpcode(device),
        switch_wrapper=DPCodeBooleanWrapper.find_dpcode(
            device, "switch", prefer_function=True
        ),
        target_humidity_wrapper=DPCodeRoundedIntegerWrapper.find_dpcode(
            device, "humidity_set", prefer_function=True
        ),
        temperature_unit=temperature_wrappers[2],
    )
