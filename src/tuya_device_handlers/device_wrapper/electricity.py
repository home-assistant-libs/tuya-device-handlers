"""Normalize electricity frames for the JSON measurement wrappers."""

from dataclasses import dataclass
from typing import Self

from tuya_sharing import CustomerDevice

from tuya_device_handlers.raw_data_model import ElectricityData
from tuya_device_handlers.type_information import (
    JsonTypeInformation,
    RawTypeInformation,
    StringTypeInformation,
)

from .sensor import (
    ElectricityApparentPowerJsonWrapper,
    ElectricityCurrentJsonWrapper,
    ElectricityPowerFactorJsonWrapper,
    ElectricityPowerJsonWrapper,
    ElectricityReactivePowerJsonWrapper,
    ElectricityVoltageJsonWrapper,
)


@dataclass(kw_only=True)
class _ElectricityTypeInformation(JsonTypeInformation):
    """Adapt a declared metering DP to the JSON field and unit contract."""

    source_type_information: (
        RawTypeInformation | StringTypeInformation | JsonTypeInformation
    )

    @classmethod
    def find_dpcode(
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        prefer_function: bool = False,
    ) -> Self | None:
        """Match DP codes in order and preserve their type conversions."""
        if dpcodes is None:
            return None
        if not isinstance(dpcodes, tuple):
            dpcodes = (dpcodes,)
        for dpcode in dpcodes:
            for dptype in (
                RawTypeInformation,
                StringTypeInformation,
                JsonTypeInformation,
            ):
                source = dptype.find_dpcode(
                    device, dpcode, prefer_function=prefer_function
                )
                if isinstance(
                    source,
                    RawTypeInformation
                    | StringTypeInformation
                    | JsonTypeInformation,
                ):
                    return cls(
                        dpcode=source.dpcode,
                        type_data=source.type_data,
                        report_type=source.report_type,
                        source_type_information=source,
                    )
        return None

    def read_device_value(
        self, device: CustomerDevice
    ) -> dict[str, float] | None:
        """Read a frame as JSON fields without changing the device status."""
        raw_value = self.source_type_information.read_device_value(device)
        if isinstance(raw_value, dict):
            return raw_value
        if not raw_value:
            return None
        value = (
            ElectricityData.from_bytes(raw_value)
            if isinstance(raw_value, bytes)
            else ElectricityData.from_hex(raw_value)
        )
        if value is None:
            # A reported but unparsable frame provides no attributes.
            return {}
        result = {
            "electricCurrent": value.current / 1000,
            "power": value.power / 1000,
            "voltage": value.voltage,
        }
        if value.reactive_power is not None:
            result["reactivePower"] = value.reactive_power / 1000
        if value.apparent_power is not None:
            result["apparentPower"] = value.apparent_power / 1000
        if value.power_factor is not None:
            result["powerFactor"] = value.power_factor
        return result


class ElectricityCurrentWrapper(ElectricityCurrentJsonWrapper):
    """Read current from a normalized Raw, String or JSON metering DP."""

    _DPTYPE = _ElectricityTypeInformation


class ElectricityPowerWrapper(ElectricityPowerJsonWrapper):
    """Read active power from a normalized metering DP."""

    _DPTYPE = _ElectricityTypeInformation


class ElectricityVoltageWrapper(ElectricityVoltageJsonWrapper):
    """Read voltage from a normalized metering DP."""

    _DPTYPE = _ElectricityTypeInformation


class ElectricityReactivePowerWrapper(ElectricityReactivePowerJsonWrapper):
    """Read reactive power from a normalized metering DP."""

    _DPTYPE = _ElectricityTypeInformation


class ElectricityApparentPowerWrapper(ElectricityApparentPowerJsonWrapper):
    """Read apparent power from a normalized metering DP."""

    _DPTYPE = _ElectricityTypeInformation


class ElectricityPowerFactorWrapper(ElectricityPowerFactorJsonWrapper):
    """Read power factor from a normalized metering DP."""

    _DPTYPE = _ElectricityTypeInformation
