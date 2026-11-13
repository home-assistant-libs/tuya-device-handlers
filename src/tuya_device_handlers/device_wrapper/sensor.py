"""Tuya device wrapper."""

from datetime import UTC, datetime, timedelta
import logging

from tuya_sharing import CustomerDevice

from tuya_device_handlers.raw_data_model import ElectricityData
from tuya_device_handlers.type_information import (
    IntegerTypeInformation,
    RawTypeInformation,
    StringTypeInformation,
)

from .common import DPCodeEnumWrapper, DPCodeIntegerWrapper
from .extended import (
    DPCodeJsonDictAttributeWrapper,
    DPCodeParsedAttributeWrapper,
)

_LOGGER = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return the current UTC time (patched in tests)."""
    return datetime.now(UTC)


class WindDirectionEnumWrapper(DPCodeEnumWrapper[float]):
    """Custom DPCode Wrapper for converting enum to wind direction."""

    _WIND_DIRECTIONS = {
        "north": 0.0,
        "north_north_east": 22.5,
        "north_east": 45.0,
        "east_north_east": 67.5,
        "east": 90.0,
        "east_south_east": 112.5,
        "south_east": 135.0,
        "south_south_east": 157.5,
        "south": 180.0,
        "south_south_west": 202.5,
        "south_west": 225.0,
        "west_south_west": 247.5,
        "west": 270.0,
        "west_north_west": 292.5,
        "north_west": 315.0,
        "north_north_west": 337.5,
    }

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read the device value for the dpcode."""
        if (status := self._read_dpcode_value(device)) is None:
            return None
        return self._WIND_DIRECTIONS.get(status)


class DeltaIntegerWrapper(DPCodeIntegerWrapper):
    """Wrapper for integer values with delta report accumulation.

    This wrapper handles sensors that report incremental (delta) values
    instead of cumulative totals. It accumulates the delta values locally
    to provide a running total.
    """

    _accumulated_value: float = 0
    _last_dp_timestamp: int | None = None

    def skip_update(
        self,
        device: CustomerDevice,
        updated_status_properties: list[str],
        dp_timestamps: dict[str, int] | None = None,
    ) -> bool:
        """Override skip_update to process delta updates.

        Processes delta accumulation before determining if
        update should be skipped.
        """
        if (
            super().skip_update(
                device, updated_status_properties, dp_timestamps
            )
            or dp_timestamps is None
            or (current_timestamp := dp_timestamps.get(self.dpcode)) is None
            or current_timestamp == self._last_dp_timestamp
            or (raw_value := self._read_dpcode_value(device)) is None
        ):
            return True

        delta = float(raw_value)
        self._accumulated_value += delta
        _LOGGER.debug(
            "Delta update for %s: +%s, total: %s",
            self.dpcode,
            delta,
            self._accumulated_value,
        )

        self._last_dp_timestamp = current_timestamp
        return False

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read device status, returning accumulated value for delta reports."""
        return self._accumulated_value


class RemainingTimeTimestampWrapper(DPCodeIntegerWrapper[datetime]):
    """Wrapper for converting a remaining time into the time it will end.

    The end time is only recalculated when the device reports a new value,
    and variations smaller than `ignored_variance` are ignored, so that the
    end time does not change every time the device counts down.
    A remaining time of 0 (no countdown running) gives None.
    """

    ignored_variance = timedelta(minutes=1)

    _TIME_UNITS = {"s": "seconds", "min": "minutes", "h": "hours"}

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init RemainingTimeTimestampWrapper."""
        super().__init__(dpcode, type_information)
        self.native_unit = None
        self._time_unit = (
            self._TIME_UNITS.get(type_information.unit)
            if type_information.unit
            else None
        )
        self._end_time: datetime | None = None
        self._initialized = False

    def _calculate_end_time(self, device: CustomerDevice) -> datetime | None:
        """Calculate the end time from the remaining time reported."""
        if (
            self._time_unit is None
            or (remaining := self._read_dpcode_value(device)) is None
            or remaining <= 0
        ):
            return None
        end_time = _utcnow() + timedelta(**{self._time_unit: remaining})
        if (
            self._end_time is not None
            and abs(end_time - self._end_time) < self.ignored_variance
        ):
            return self._end_time
        return end_time

    def skip_update(
        self,
        device: CustomerDevice,
        updated_status_properties: list[str],
        dp_timestamps: dict[str, int] | None = None,
    ) -> bool:
        """Recalculate the end time, and skip if it did not change."""
        if super().skip_update(
            device, updated_status_properties, dp_timestamps
        ):
            return True
        end_time = self._calculate_end_time(device)
        if self._initialized and end_time == self._end_time:
            return True
        self._end_time = end_time
        self._initialized = True
        return False

    def read_device_status(self, device: CustomerDevice) -> datetime | None:
        """Return the end time."""
        if not self._initialized:
            self._end_time = self._calculate_end_time(device)
            self._initialized = True
        return self._end_time


class ElectricityCurrentJsonWrapper(DPCodeJsonDictAttributeWrapper):
    """Custom DPCode Wrapper for extracting electricity current from JSON."""

    _ATTRIBUTE_NAME = "electricCurrent"
    native_unit = "A"


class ElectricityPowerJsonWrapper(DPCodeJsonDictAttributeWrapper):
    """Custom DPCode Wrapper for extracting electricity power from JSON."""

    _ATTRIBUTE_NAME = "power"
    native_unit = "kW"


class ElectricityVoltageJsonWrapper(DPCodeJsonDictAttributeWrapper):
    """Custom DPCode Wrapper for extracting electricity voltage from JSON."""

    _ATTRIBUTE_NAME = "voltage"
    native_unit = "V"


class ElectricityReactivePowerJsonWrapper(DPCodeJsonDictAttributeWrapper):
    """Custom DPCode Wrapper for extracting reactive power from JSON."""

    _ATTRIBUTE_NAME = "reactivePower"
    native_unit = "kvar"


class ElectricityApparentPowerJsonWrapper(DPCodeJsonDictAttributeWrapper):
    """Custom DPCode Wrapper for extracting apparent power from JSON."""

    _ATTRIBUTE_NAME = "apparentPower"
    native_unit = "kVA"


class ElectricityPowerFactorJsonWrapper(DPCodeJsonDictAttributeWrapper):
    """Custom DPCode Wrapper for extracting power factor from JSON."""

    _ATTRIBUTE_NAME = "powerFactor"


class _ElectricityRawWrapper(
    DPCodeParsedAttributeWrapper[bytes, RawTypeInformation, ElectricityData]
):
    """Base wrapper for an electricity attribute in a base64 payload."""

    _DPTYPE = RawTypeInformation

    @classmethod
    def _parse(cls, raw_value: bytes) -> ElectricityData | None:
        """Parse the base64 payload."""
        return ElectricityData.from_bytes(raw_value)


class _ElectricityHexStringWrapper(
    DPCodeParsedAttributeWrapper[str, StringTypeInformation, ElectricityData]
):
    """Base wrapper for an electricity attribute in a hex string payload."""

    _DPTYPE = StringTypeInformation

    @classmethod
    def _parse(cls, raw_value: str) -> ElectricityData | None:
        """Parse the hex string payload."""
        return ElectricityData.from_hex(raw_value)


class ElectricityCurrentRawWrapper(_ElectricityRawWrapper):
    """Custom DPCode Wrapper for extracting electricity current from base64."""

    _ATTRIBUTE_NAME = "current"
    native_unit = "mA"


class ElectricityPowerRawWrapper(_ElectricityRawWrapper):
    """Custom DPCode Wrapper for extracting electricity power from base64."""

    _ATTRIBUTE_NAME = "power"
    native_unit = "W"


class ElectricityVoltageRawWrapper(_ElectricityRawWrapper):
    """Custom DPCode Wrapper for extracting electricity voltage from base64."""

    _ATTRIBUTE_NAME = "voltage"
    native_unit = "V"


class ElectricityReactivePowerRawWrapper(_ElectricityRawWrapper):
    """Custom DPCode Wrapper for extracting reactive power from base64."""

    _ATTRIBUTE_NAME = "reactive_power"
    native_unit = "var"
    suggested_unit = "kvar"


class ElectricityApparentPowerRawWrapper(_ElectricityRawWrapper):
    """Custom DPCode Wrapper for extracting apparent power from base64."""

    _ATTRIBUTE_NAME = "apparent_power"
    native_unit = "VA"
    suggested_unit = "kVA"


class ElectricityPowerFactorRawWrapper(_ElectricityRawWrapper):
    """Custom DPCode Wrapper for extracting power factor from base64."""

    _ATTRIBUTE_NAME = "power_factor"


class ElectricityCurrentHexStringWrapper(_ElectricityHexStringWrapper):
    """Custom DPCode Wrapper for extracting current from a hex string."""

    _ATTRIBUTE_NAME = "current"
    native_unit = "mA"
    suggested_unit = "A"


class ElectricityPowerHexStringWrapper(_ElectricityHexStringWrapper):
    """Custom DPCode Wrapper for extracting power from a hex string."""

    _ATTRIBUTE_NAME = "power"
    native_unit = "W"
    suggested_unit = "kW"


class ElectricityVoltageHexStringWrapper(_ElectricityHexStringWrapper):
    """Custom DPCode Wrapper for extracting voltage from a hex string."""

    _ATTRIBUTE_NAME = "voltage"
    native_unit = "V"


class ElectricityReactivePowerHexStringWrapper(_ElectricityHexStringWrapper):
    """Custom DPCode Wrapper for extracting reactive power from a hex string."""

    _ATTRIBUTE_NAME = "reactive_power"
    native_unit = "var"
    suggested_unit = "kvar"


class ElectricityApparentPowerHexStringWrapper(_ElectricityHexStringWrapper):
    """Custom DPCode Wrapper for extracting apparent power from a hex string."""

    _ATTRIBUTE_NAME = "apparent_power"
    native_unit = "VA"
    suggested_unit = "kVA"


class ElectricityPowerFactorHexStringWrapper(_ElectricityHexStringWrapper):
    """Custom DPCode Wrapper for extracting power factor from a hex string."""

    _ATTRIBUTE_NAME = "power_factor"
