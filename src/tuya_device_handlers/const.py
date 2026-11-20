"""Constants for Tuya device handlers."""

from __future__ import annotations

from enum import IntFlag, StrEnum

# Dictionary to track logged warnings to avoid spamming logs
# Keyed by device ID
DEVICE_WARNINGS: dict[str, set[str]] = {}

# Aliases for temperature units to handle variations in device reporting
CELSIUS_ALIASES = {"°c", "c", "celsius", "℃"}
FAHRENHEIT_ALIASES = {"°f", "f", "fahrenheit", "℉"}


class ColorTempScale(StrEnum):
    """Scale used by a device for its color temperature datapoint."""

    MIRED = "mired"
    """The raw range maps linearly onto mireds (Tuya default)."""

    KELVIN = "kelvin"
    """The raw range maps linearly onto Kelvin."""


class DPMode(IntFlag):
    """Data point modes."""

    READ = 1
    WRITE = 2


class DPType(StrEnum):
    """Data point types."""

    BITMAP = "Bitmap"
    BOOLEAN = "Boolean"
    ENUM = "Enum"
    INTEGER = "Integer"
    JSON = "Json"
    RAW = "Raw"
    STRING = "String"

    @staticmethod
    def try_parse(current_type: str) -> DPType | None:
        """Try to parse a string into a DPType.

        The cloud is known to return ill-formed values, for example uppercase
        (`"ENUM"` instead of `"Enum"`) or unrelated aliases (`"bool"`).
        """
        for candidate in (current_type, current_type.capitalize()):
            try:
                return DPType(candidate)
            except ValueError:
                continue
        return _DPTYPE_MAPPING.get(current_type.lower())


_DPTYPE_MAPPING: dict[str, DPType] = {
    "bitmap": DPType.BITMAP,
    "bool": DPType.BOOLEAN,
    "enum": DPType.ENUM,
    "json": DPType.JSON,
    "raw": DPType.RAW,
    "string": DPType.STRING,
    "value": DPType.INTEGER,
}
