"""Quirks registry."""

from collections.abc import Sequence
import logging
import pathlib
from typing import Protocol, Self

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.definition.alarm_control_panel import (
    AlarmControlPanelQuirk,
)
from tuya_device_handlers.definition.binary_sensor import BinarySensorQuirk
from tuya_device_handlers.definition.button import ButtonQuirk
from tuya_device_handlers.definition.camera import CameraQuirk
from tuya_device_handlers.definition.climate import ClimateQuirk
from tuya_device_handlers.definition.cover import CoverQuirk
from tuya_device_handlers.definition.event import EventQuirk
from tuya_device_handlers.definition.fan import FanQuirk
from tuya_device_handlers.definition.humidifier import HumidifierQuirk
from tuya_device_handlers.definition.light import LightQuirk
from tuya_device_handlers.definition.number import NumberQuirk
from tuya_device_handlers.definition.select import SelectQuirk
from tuya_device_handlers.definition.sensor import SensorQuirk
from tuya_device_handlers.definition.siren import SirenQuirk
from tuya_device_handlers.definition.switch import SwitchQuirk
from tuya_device_handlers.definition.vacuum import VacuumQuirk
from tuya_device_handlers.definition.valve import ValveQuirk

_LOGGER = logging.getLogger(__name__)


class DeviceQuirkProtocol(Protocol):
    """Protocol for a Tuya device quirk."""

    @property
    def alarm_control_panel_quirks(
        self,
    ) -> Sequence[AlarmControlPanelQuirk] | None: ...
    @property
    def binary_sensor_quirks(self) -> Sequence[BinarySensorQuirk] | None: ...
    @property
    def button_quirks(self) -> Sequence[ButtonQuirk] | None: ...
    @property
    def camera_quirks(self) -> Sequence[CameraQuirk] | None: ...
    @property
    def climate_quirks(self) -> Sequence[ClimateQuirk] | None: ...
    @property
    def cover_quirks(self) -> Sequence[CoverQuirk] | None: ...
    @property
    def event_quirks(self) -> Sequence[EventQuirk] | None: ...
    @property
    def fan_quirks(self) -> Sequence[FanQuirk] | None: ...
    @property
    def humidifier_quirks(self) -> Sequence[HumidifierQuirk] | None: ...
    @property
    def light_quirks(self) -> Sequence[LightQuirk] | None: ...
    @property
    def number_quirks(self) -> Sequence[NumberQuirk] | None: ...
    @property
    def select_quirks(self) -> Sequence[SelectQuirk] | None: ...
    @property
    def sensor_quirks(self) -> Sequence[SensorQuirk] | None: ...
    @property
    def siren_quirks(self) -> Sequence[SirenQuirk] | None: ...
    @property
    def switch_quirks(self) -> Sequence[SwitchQuirk] | None: ...
    @property
    def vacuum_quirks(self) -> Sequence[VacuumQuirk] | None: ...
    @property
    def valve_quirks(self) -> Sequence[ValveQuirk] | None: ...

    @property
    def quirk_file(self) -> pathlib.Path: ...
    @property
    def quirk_file_line(self) -> int: ...


class QuirksRegistry:
    """Registry for Tuya quirks."""

    instance: Self

    _quirks: dict[str, dict[str, DeviceQuirkProtocol]]

    def __new__(cls) -> Self:
        """Create a new class."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        """Initialize the registry."""
        self._quirks = {}

    def register(
        self,
        category: str,
        product_id: str,
        quirk: DeviceQuirkProtocol,
    ) -> None:
        """Register a quirk for a specific device type."""
        self._quirks.setdefault(category, {})[product_id] = quirk

    def get_quirk_for_device(
        self, device: CustomerDevice
    ) -> DeviceQuirkProtocol | None:
        """Get the quirk for a specific device."""
        return self._quirks.get(device.category, {}).get(device.product_id)

    def purge_custom_quirks(self, custom_quirks_root: str) -> None:
        """Purge custom quirks from the registry."""
        for category_quirks in self._quirks.values():
            to_remove = []
            for product_id, quirk in category_quirks.items():
                if quirk.quirk_file.is_relative_to(custom_quirks_root):
                    to_remove.append(product_id)

            for product_id in to_remove:
                _LOGGER.debug("Removing stale custom quirk: %s", product_id)
                category_quirks.pop(product_id)
