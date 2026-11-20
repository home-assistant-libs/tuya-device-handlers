"""Tuya climate definition."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tuya_sharing import CustomerDevice

from tuya_device_handlers.const import CELSIUS_ALIASES, FAHRENHEIT_ALIASES
from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.climate import (
    DefaultClimateActionWrapper,
    DefaultHVACModeWrapper,
    DefaultPresetModeWrapper,
    SwingModeCompositeWrapper,
)
from tuya_device_handlers.device_wrapper.common import (
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
    DPCodeIntegerEnumWrapper,
    DPCodeIntegerWrapper,
    DPCodeStringWrapper,
)
from tuya_device_handlers.device_wrapper.exception import (
    SetValueOutOfRangeError,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeRoundedIntegerWrapper,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaClimateAction,
    TuyaClimateHVACMode,
    TuyaClimateSwingMode,
    TuyaUnitOfTemperature,
)
from tuya_device_handlers.type_information import IntegerEnumTypeInformation

from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class ClimateDefinition:
    """Definition for a climate entity."""

    action_wrapper: DeviceWrapper[TuyaClimateAction] | None = None
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


def get_temperature_wrappers(
    *,
    temp_current: DPCodeIntegerWrapper | None,
    temp_current_f: DPCodeIntegerWrapper | None,
    temp_set: DPCodeIntegerWrapper | None,
    temp_set_f: DPCodeIntegerWrapper | None,
    system_temperature_unit: TuyaUnitOfTemperature,
) -> tuple[
    DPCodeIntegerWrapper | None,
    DPCodeIntegerWrapper | None,
    TuyaUnitOfTemperature,
]:
    """Get temperature wrappers for current and set temperatures."""
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
    if system_temperature_unit == TuyaUnitOfTemperature.FAHRENHEIT:  # noqa: SIM102
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


def _get_default_temperature_wrappers(
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

    return get_temperature_wrappers(
        temp_current=temp_current,
        temp_current_f=temp_current_f,
        temp_set=temp_set,
        temp_set_f=temp_set_f,
        system_temperature_unit=system_temperature_unit,
    )


_INFRARED_AC_MODE_TO_HVACMODE = {
    0: TuyaClimateHVACMode.COOL,
    1: TuyaClimateHVACMode.HEAT,
    2: TuyaClimateHVACMode.HEAT_COOL,
    3: TuyaClimateHVACMode.FAN_ONLY,
    4: TuyaClimateHVACMode.DRY,
}
_INFRARED_AC_FAN_MODES = {
    0: "auto",
    1: "low",
    2: "medium",
    3: "high",
}


class InfraredAcPowerWrapper(DeviceWrapper[bool]):
    """Power wrapper for IR air conditioners.

    IR air conditioners are virtual devices driven by an IR hub. Instead of a
    boolean switch they use two write-only string datapoints (`PowerOn` and
    `PowerOff`). The hub does report the resulting power state as the
    `power` status datapoint.
    """

    def __init__(self, *, power_on: str, power_off: str) -> None:
        """Init InfraredAcPowerWrapper."""
        self.power_on = power_on
        self.power_off = power_off

    def read_device_status(self, device: CustomerDevice) -> bool | None:
        """Return the power state reported by the hub, if available."""
        raw_value = device.status.get("power")
        if raw_value is None:
            return None
        return bool(raw_value)

    def get_update_commands(
        self, device: CustomerDevice, value: bool
    ) -> list[dict[str, Any]]:
        """Return the power command for the desired state."""
        code = self.power_on if value else self.power_off
        return [{"code": code, "value": code}]


class InfraredAcHVACModeWrapper(DPCodeIntegerEnumWrapper[TuyaClimateHVACMode]):
    """HVAC mode wrapper for IR air conditioners (`M`)."""

    options: list[str]

    def __init__(
        self, dpcode: str, type_information: IntegerEnumTypeInformation
    ) -> None:
        """Init InfraredAcHVACModeWrapper."""
        super().__init__(dpcode, type_information)
        self.options = [
            str(hvac_mode)
            for raw_value in type_information.range
            if (hvac_mode := _INFRARED_AC_MODE_TO_HVACMODE.get(raw_value))
        ]

    def read_device_status(
        self, device: CustomerDevice
    ) -> TuyaClimateHVACMode | None:
        """Return the HVAC mode reported by the hub, if available."""
        raw_value = device.status.get("mode")
        if raw_value is None:
            return None
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            return None
        return _INFRARED_AC_MODE_TO_HVACMODE.get(value)

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: TuyaClimateHVACMode
    ) -> int:
        """Convert the HVAC mode to the raw `M` value."""
        for raw_value, hvac_mode in _INFRARED_AC_MODE_TO_HVACMODE.items():
            if hvac_mode == value and raw_value in self.values:
                return raw_value
        msg = f"Unsupported HVAC mode `{value}`"
        raise SetValueOutOfRangeError(msg)


class InfraredAcFanModeWrapper(DPCodeIntegerEnumWrapper[str]):
    """Fan mode wrapper for IR air conditioners (`F`)."""

    options: list[str]

    def __init__(
        self, dpcode: str, type_information: IntegerEnumTypeInformation
    ) -> None:
        """Init InfraredAcFanModeWrapper."""
        super().__init__(dpcode, type_information)
        self.options = [
            fan_mode
            for raw_value in type_information.range
            if (fan_mode := _INFRARED_AC_FAN_MODES.get(raw_value))
        ]

    def read_device_status(self, device: CustomerDevice) -> str | None:
        """Return the fan mode reported by the hub, if available."""
        raw_value = device.status.get("wind")
        if raw_value is None:
            return None
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            return None
        return _INFRARED_AC_FAN_MODES.get(value)

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: str
    ) -> int:
        """Convert the fan mode to the raw `F` value."""
        for raw_value, fan_mode in _INFRARED_AC_FAN_MODES.items():
            if fan_mode == value and raw_value in self.values:
                return raw_value
        msg = f"Unsupported fan mode `{value}`"
        raise SetValueOutOfRangeError(msg)


class InfraredAcTemperatureWrapper(DPCodeIntegerEnumWrapper[float]):
    """Set temperature wrapper for IR air conditioners (`T`)."""

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Return the temperature reported by the hub, if available."""
        raw_value = device.status.get("temp")
        if raw_value is None:
            return None
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            return None
        if not (
            self.type_information.min <= value <= self.type_information.max
        ):
            return None
        return value


def get_infrared_ac_definition(
    device: CustomerDevice,
) -> ClimateDefinition | None:
    """Get the climate definition for an IR air conditioner.

    IR air conditioners are driven through write-only commands (`PowerOn`,
    `PowerOff`, `M`, `T` and `F`), but the hub reports the resulting state
    as `power`, `mode`, `temp` and `wind` status datapoints, which the
    wrappers below read back.
    """
    if not DPCodeStringWrapper.find_dpcode(
        device, "PowerOn", prefer_function=True
    ) or not DPCodeStringWrapper.find_dpcode(
        device, "PowerOff", prefer_function=True
    ):
        return None

    return ClimateDefinition(
        current_humidity_wrapper=None,
        current_temperature_wrapper=None,
        fan_mode_wrapper=InfraredAcFanModeWrapper.find_dpcode(
            device, "F", prefer_function=True
        ),
        hvac_mode_wrapper=InfraredAcHVACModeWrapper.find_dpcode(
            device, "M", prefer_function=True
        ),
        preset_wrapper=None,
        set_temperature_wrapper=InfraredAcTemperatureWrapper.find_dpcode(
            device, "T", prefer_function=True
        ),
        swing_wrapper=None,
        switch_wrapper=InfraredAcPowerWrapper(
            power_on="PowerOn", power_off="PowerOff"
        ),
        target_humidity_wrapper=None,
        temperature_unit=TuyaUnitOfTemperature.CELSIUS,
    )


def get_default_definition(
    device: CustomerDevice, system_temperature_unit: TuyaUnitOfTemperature
) -> ClimateDefinition:
    """Get the default climate definition for a device."""
    current_temperature_wrapper, set_temperature_wrapper, temperature_unit = (
        _get_default_temperature_wrappers(device, system_temperature_unit)
    )
    return ClimateDefinition(
        action_wrapper=DefaultClimateActionWrapper.find_dpcode(
            device, ("work_state", "work_state_e")
        ),
        current_humidity_wrapper=DPCodeRoundedIntegerWrapper.find_dpcode(
            device, "humidity_current"
        ),
        current_temperature_wrapper=current_temperature_wrapper,
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
        set_temperature_wrapper=set_temperature_wrapper,
        swing_wrapper=SwingModeCompositeWrapper.find_dpcode(device),
        switch_wrapper=DPCodeBooleanWrapper.find_dpcode(
            device, ("switch", "power_switch"), prefer_function=True
        ),
        target_humidity_wrapper=DPCodeRoundedIntegerWrapper.find_dpcode(
            device, "humidity_set", prefer_function=True
        ),
        temperature_unit=temperature_unit,
    )
