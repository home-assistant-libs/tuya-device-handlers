"""Helpers for quirk fan tests.

The category set below mirrors the ``TUYA_SUPPORT_TYPE`` set in Home
Assistant core, so tests can assert that a quirk produces the fan core
would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/fan.py
"""

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.fan import (
    FanDefinition,
    get_default_definition,
)

# Categories Home Assistant core builds a fan entity for, mirroring the
# ``TUYA_SUPPORT_TYPE`` set in Home Assistant core.
_FANS: frozenset[str] = frozenset(
    {
        "fs",  # Fan
        "fsd",  # Fan with light
        "fskg",  # Fan wall switch
        "kj",  # Air Purifier
        "cs",  # Dehumidifier
    }
)


def get_fan_default_definition(
    device: CustomerDevice,
) -> FanDefinition | None:
    """Get the default fan definition Home Assistant builds for a device."""
    if device.category not in _FANS:
        return None
    return get_default_definition(device)
