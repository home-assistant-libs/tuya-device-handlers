"""Tuya device wrapper."""

import logging

from tuya_sharing import CustomerDevice

from tuya_device_handlers.raw_data_model import ElectricityData

from .common import (
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
    DPCodeJsonWrapper,
    DPCodeRawWrapper,
)

_LOGGER = logging.getLogger(__name__)


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


class ElectricityCurrentJsonWrapper(DPCodeJsonWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity current from JSON."""

    native_unit = "A"

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read the device value for the dpcode."""
        if (status := self._read_dpcode_value(device)) is None:
            return None
        return status.get("electricCurrent")


class ElectricityPowerJsonWrapper(DPCodeJsonWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity power from JSON."""

    native_unit = "kW"

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read the device value for the dpcode."""
        if (status := self._read_dpcode_value(device)) is None:
            return None
        return status.get("power")


class ElectricityVoltageJsonWrapper(DPCodeJsonWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity voltage from JSON."""

    native_unit = "V"

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read the device value for the dpcode."""
        if (status := self._read_dpcode_value(device)) is None:
            return None
        return status.get("voltage")


class ElectricityCurrentRawWrapper(DPCodeRawWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity current from base64."""

    native_unit = "mA"
    suggested_unit = "A"

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read the device value for the dpcode."""
        if (raw_value := self._read_dpcode_value(device)) is None or (
            value := ElectricityData.from_bytes(raw_value)
        ) is None:
            return None
        return value.current


class ElectricityPowerRawWrapper(DPCodeRawWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity power from base64."""

    native_unit = "W"
    suggested_unit = "kW"

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read the device value for the dpcode."""
        if (raw_value := self._read_dpcode_value(device)) is None or (
            value := ElectricityData.from_bytes(raw_value)
        ) is None:
            return None
        return value.power


class ElectricityVoltageRawWrapper(DPCodeRawWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity voltage from base64."""

    native_unit = "V"

    def read_device_status(self, device: CustomerDevice) -> float | None:
        """Read the device value for the dpcode."""
        if (raw_value := self._read_dpcode_value(device)) is None or (
            value := ElectricityData.from_bytes(raw_value)
        ) is None:
            return None
        return value.voltage
