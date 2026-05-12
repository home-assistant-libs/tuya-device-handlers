"""Tuya device wrapper."""


class SetValueOutOfRangeError(ValueError):
    """Attempted to send an invalid value to Tuya data point."""
