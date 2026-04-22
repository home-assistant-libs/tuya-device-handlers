"""Constants for Tuya device handlers."""

from __future__ import annotations

from enum import IntFlag, StrEnum

CELSIUS_ALIASES = {"°c", "c", "celsius", "℃"}
FAHRENHEIT_ALIASES = {"°f", "f", "fahrenheit", "℉"}


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
        try:
            return DPType(current_type)
        except ValueError:
            # Sometimes, we get ill-formed DPTypes from the cloud,
            # this fixes them and maps them to the correct DPType.
            return _DPTYPE_MAPPING.get(current_type)


_DPTYPE_MAPPING: dict[str, DPType] = {
    "bitmap": DPType.BITMAP,
    "bool": DPType.BOOLEAN,
    "enum": DPType.ENUM,
    "json": DPType.JSON,
    "raw": DPType.RAW,
    "string": DPType.STRING,
    "value": DPType.INTEGER,
}
