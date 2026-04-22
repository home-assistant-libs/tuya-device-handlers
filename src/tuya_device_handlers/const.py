"""Constants for Tuya device handlers."""

from __future__ import annotations

from enum import StrEnum

CELSIUS_ALIASES = {"°c", "c", "celsius", "℃"}
FAHRENHEIT_ALIASES = {"°f", "f", "fahrenheit", "℉"}


class DPMode(StrEnum):
    """Data point modes."""

    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    READ_WRITE = "read_write"


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
