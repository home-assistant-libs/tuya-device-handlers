"""Tuya device wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .type_information import IntegerTypeInformation


@dataclass(kw_only=True)
class RemapHelper:
    """Helper class for remapping values."""

    source_min: int
    source_max: int
    target_min: float
    target_max: float

    @classmethod
    def from_type_information(
        cls,
        type_information: IntegerTypeInformation,
        target_min: float,
        target_max: float,
    ) -> RemapHelper:
        """Create RemapHelper from IntegerTypeInformation."""
        return cls(
            source_min=type_information.min,
            source_max=type_information.max,
            target_min=target_min,
            target_max=target_max,
        )

    @classmethod
    def from_function_data(
        cls, function_data: dict[str, Any], target_min: int, target_max: int
    ) -> RemapHelper:
        """Create RemapHelper from function_data."""
        return cls(
            source_min=function_data["min"],
            source_max=function_data["max"],
            target_min=target_min,
            target_max=target_max,
        )

    def remap_value_to(self, value: float, *, reverse: bool = False) -> float:
        """Remap a value from this range to a new range."""
        return self.remap_value(
            value,
            self.source_min,
            self.source_max,
            self.target_min,
            self.target_max,
            reverse=reverse,
        )

    def remap_value_from(self, value: float, *, reverse: bool = False) -> float:
        """Remap a value from its current range to this range."""
        return self.remap_value(
            value,
            self.target_min,
            self.target_max,
            self.source_min,
            self.source_max,
            reverse=reverse,
        )

    @staticmethod
    def remap_value(
        value: float,
        from_min: float,
        from_max: float,
        to_min: float,
        to_max: float,
        *,
        reverse: bool = False,
    ) -> float:
        """Remap a value from its current range, to a new range."""
        if reverse:
            value = from_max - value + from_min
        return ((value - from_min) / (from_max - from_min)) * (
            to_max - to_min
        ) + to_min
