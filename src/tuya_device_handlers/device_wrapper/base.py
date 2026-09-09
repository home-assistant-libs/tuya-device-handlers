"""Tuya device wrapper."""

from typing import Any

from tuya_sharing import CustomerDevice


class DeviceWrapper[T]:
    """Base device wrapper."""

    native_unit: str | None = None
    suggested_unit: str | None = None

    max_value: float
    min_value: float
    value_step: float

    options: list[str]

    def initialize(self, device: CustomerDevice) -> None:
        """Initialize the wrapper with device data.

        Called when the entity is added to Home Assistant.
        Override in subclasses to perform initialization logic.
        """

    def skip_update(
        self,
        device: CustomerDevice,
        updated_status_properties: list[str],
        dp_timestamps: dict[str, int] | None = None,
    ) -> bool:
        """Determine if the wrapper should skip an update.

        The default is to always skip, unless overridden in subclasses.
        """
        return True

    def read_device_status(self, device: CustomerDevice) -> T | None:
        """Read device status and convert to a Home Assistant value."""
        raise NotImplementedError

    def get_update_commands(
        self, device: CustomerDevice, value: T
    ) -> list[dict[str, Any]]:
        """Generate update commands for a Home Assistant action."""
        raise NotImplementedError
