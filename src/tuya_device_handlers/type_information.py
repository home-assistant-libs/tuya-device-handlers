"""Type information classes for the Tuya integration."""

from dataclasses import dataclass
import json
from typing import Any, ClassVar, Self, cast

from tuya_sharing import CustomerDevice

from .const import DPType


@dataclass(kw_only=True)
class TypeInformation:
    """Type information.

    As provided by the SDK, from `device.function` / `device.status_range`.
    """

    _DPTYPE: ClassVar[DPType]
    dpcode: str
    type_data: str

    @classmethod
    def _from_json(
        cls, dpcode: str, type_data: str, *, report_type: str | None
    ) -> Self | None:
        """Load JSON string and return a TypeInformation object."""
        return cls(dpcode=dpcode, type_data=type_data)

    @classmethod
    def find_dpcode(
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        prefer_function: bool = False,
    ) -> Self | None:
        """Find type information for a matching DP code available for this device."""
        if dpcodes is None:
            return None

        if not isinstance(dpcodes, tuple):
            dpcodes = (dpcodes,)

        lookup_tuple = (
            (device.function, device.status_range)
            if prefer_function
            else (device.status_range, device.function)
        )

        for dpcode in dpcodes:
            report_type = (
                status_range.report_type
                if (status_range := device.status_range.get(dpcode))
                else None
            )
            for device_specs in lookup_tuple:
                if (
                    (current_definition := device_specs.get(dpcode))
                    and DPType.try_parse(current_definition.type) is cls._DPTYPE
                    and (
                        type_information := cls._from_json(
                            dpcode=dpcode,
                            type_data=current_definition.values,
                            report_type=report_type,
                        )
                    )
                ):
                    return type_information

        return None


@dataclass(kw_only=True)
class BitmapTypeInformation(TypeInformation):
    """Bitmap type information."""

    _DPTYPE = DPType.BITMAP

    label: list[str]

    @classmethod
    def _from_json(
        cls, dpcode: str, type_data: str, *, report_type: str | None
    ) -> Self | None:
        """Load JSON string and return a BitmapTypeInformation object."""
        if not (parsed := cast(dict[str, Any] | None, json.loads(type_data))):
            return None
        return cls(
            dpcode=dpcode,
            type_data=type_data,
            label=parsed["label"],
        )


@dataclass(kw_only=True)
class BooleanTypeInformation(TypeInformation):
    """Boolean type information."""

    _DPTYPE = DPType.BOOLEAN


@dataclass(kw_only=True)
class EnumTypeInformation(TypeInformation):
    """Enum type information."""

    _DPTYPE = DPType.ENUM

    range: list[str]

    @classmethod
    def _from_json(
        cls, dpcode: str, type_data: str, *, report_type: str | None
    ) -> Self | None:
        """Load JSON string and return an EnumTypeInformation object."""
        if not (parsed := json.loads(type_data)):
            return None
        return cls(
            dpcode=dpcode,
            type_data=type_data,
            **cast(dict[str, list[str]], parsed),
        )


@dataclass(kw_only=True)
class IntegerTypeInformation(TypeInformation):
    """Integer type information."""

    _DPTYPE = DPType.INTEGER

    min: int
    max: int
    scale: int
    step: int
    unit: str | None = None
    report_type: str | None

    def scale_value(self, value: int) -> float:
        """Scale a value."""
        return value / (10**self.scale)  # type: ignore[no-any-return]

    def scale_value_back(self, value: float) -> int:
        """Return raw value for scaled."""
        return round(value * (10**self.scale))  # type: ignore[no-any-return]

    @classmethod
    def _from_json(
        cls, dpcode: str, type_data: str, *, report_type: str | None
    ) -> Self | None:
        """Load JSON string and return an IntegerTypeInformation object."""
        if not (parsed := cast(dict[str, Any] | None, json.loads(type_data))):
            return None

        return cls(
            dpcode=dpcode,
            type_data=type_data,
            min=int(parsed["min"]),
            max=int(parsed["max"]),
            scale=int(parsed["scale"]),
            step=int(parsed["step"]),
            unit=parsed.get("unit"),
            report_type=report_type,
        )


@dataclass(kw_only=True)
class JsonTypeInformation(TypeInformation):
    """Json type information."""

    _DPTYPE = DPType.JSON


@dataclass(kw_only=True)
class RawTypeInformation(TypeInformation):
    """Raw type information."""

    _DPTYPE = DPType.RAW


@dataclass(kw_only=True)
class StringTypeInformation(TypeInformation):
    """String type information."""

    _DPTYPE = DPType.STRING
