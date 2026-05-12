"""Tuya entity definition."""

from dataclasses import dataclass


@dataclass(kw_only=True)
class BaseEntityQuirk:
    """Base quirk for a Tuya entity."""

    key: str
