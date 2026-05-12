"""Tuya device handler."""

from .registry import QuirksRegistry

__all__ = [
    "TUYA_QUIRKS_REGISTRY",
]

TUYA_QUIRKS_REGISTRY = QuirksRegistry()
