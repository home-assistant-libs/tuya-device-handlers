"""Quirks registry."""

import logging
import pathlib
from typing import Any, Protocol, Self

from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

from tuya_device_handlers.device_wrapper.base import DeviceWrapper
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    FeederSchedule,
)

_LOGGER = logging.getLogger(__name__)


class DeviceQuirkProtocol(Protocol):
    """Protocol for a Tuya device quirk."""

    original_function: dict[str, DeviceFunction]
    original_local_strategy: dict[int, dict[str, Any]]
    original_status_range: dict[str, DeviceStatusRange]

    @property
    def quirk_file(self) -> pathlib.Path: ...
    @property
    def quirk_file_line(self) -> int: ...

    def initialise_device(self, device: CustomerDevice) -> None: ...

    def get_feeder_schedules_wrapper(
        self, device: CustomerDevice
    ) -> DeviceWrapper[list[FeederSchedule]] | None: ...


class QuirksRegistry:
    """Registry for Tuya quirks."""

    instance: Self

    _quirks: dict[str, DeviceQuirkProtocol]

    def __new__(cls) -> Self:
        """Create a new class."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        """Initialize the registry."""
        if not hasattr(self, "_quirks"):
            self._quirks = {}

    def register(
        self,
        product_id: str,
        quirk: DeviceQuirkProtocol,
    ) -> None:
        """Register a quirk for a specific device type."""
        self._quirks[product_id] = quirk

    def get_quirk_for_device(
        self, device: CustomerDevice
    ) -> DeviceQuirkProtocol | None:
        """Get the quirk for a specific device."""
        return self._quirks.get(device.product_id)

    def initialise_device_quirk(self, device: CustomerDevice) -> None:
        """Apply the quirk to a specific device."""
        if quirk := self._quirks.get(device.product_id):
            quirk.initialise_device(device)

    def purge_custom_quirks(self, custom_quirks_root: str) -> None:
        """Purge custom quirks from the registry."""
        to_remove = [
            product_id
            for product_id, quirk in self._quirks.items()
            if quirk.quirk_file.is_relative_to(custom_quirks_root)
        ]

        for product_id in to_remove:
            _LOGGER.debug("Removing stale custom quirk: %s", product_id)
            self._quirks.pop(product_id, None)
