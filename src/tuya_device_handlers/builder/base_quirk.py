"""Base quirk definition."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import inspect
import pathlib
from typing import TYPE_CHECKING, Any, Self

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.const import DPType
from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.helpers import (
    TuyaClimateHVACMode,
    TuyaCoverDeviceClass,
    TuyaEntityCategory,
    TuyaSensorDeviceClass,
    TuyaSensorStateClass,
    TuyaSwitchDeviceClass,
)

if TYPE_CHECKING:
    from tuya_device_handlers.registry import QuirksRegistry


type DeviceWrapperGenerator = Callable[
    [CustomerDevice], DeviceWrapper[Any] | None
]


def _none_type_generator(device: CustomerDevice) -> None:
    return None


@dataclass
class BaseTuyaDefinition:
    """Definition for a Tuya entity."""

    key: str

    device_class: str | None = None
    entity_category: TuyaEntityCategory | None = None
    entity_registry_enabled_default: bool = True
    entity_registry_visible_default: bool = True
    icon: str | None = None
    translation_key: str | None = None
    translation_placeholders: dict[str, str] | None = None
    translation_string: str | None = None
    translation_states: dict[str, str] | None = None


@dataclass(kw_only=True)
class TuyaClimateDefinition(BaseTuyaDefinition):
    """Definition for a climate entity."""

    switch_only_hvac_mode: TuyaClimateHVACMode

    current_temperature_dp_type: DeviceWrapperGenerator
    target_temperature_dp_type: DeviceWrapperGenerator


@dataclass(kw_only=True)
class TuyaCoverDefinition(BaseTuyaDefinition):
    """Definition for a cover entity."""

    device_class: TuyaCoverDeviceClass | None = None

    get_state_dp_type: DeviceWrapperGenerator
    set_state_dp_type: DeviceWrapperGenerator
    get_position_dp_type: DeviceWrapperGenerator
    set_position_dp_type: DeviceWrapperGenerator


@dataclass(kw_only=True)
class TuyaSelectDefinition(BaseTuyaDefinition):
    """Definition for a select entity."""

    dp_type: DeviceWrapperGenerator


@dataclass(kw_only=True)
class TuyaSensorDefinition(BaseTuyaDefinition):
    """Definition for a sensor entity."""

    dp_type: DeviceWrapperGenerator
    device_class: TuyaSensorDeviceClass | None = None
    state_class: TuyaSensorStateClass | None = None
    suggested_unit: str | None = None


@dataclass(kw_only=True)
class TuyaSwitchDefinition(BaseTuyaDefinition):
    """Definition for a switch entity."""

    dp_type: DeviceWrapperGenerator
    device_class: TuyaSwitchDeviceClass | None = None


@dataclass(kw_only=True)
class DatapointDefinition:
    """Definition for a Tuya datapoint."""

    dpid: int
    dpcode: str
    dptype: DPType
    enum_range: list[str] | None = None
    int_range: dict[str, Any] | None = None
    label_range: list[str] | None = None


class TuyaDeviceQuirk:
    """Quirk for Tuya device."""

    def __init__(self) -> None:
        """Initialize the quirk."""
        self._applies_to: list[tuple[str, str]] = []

        self.datapoint_definitions: dict[int, DatapointDefinition] = {}

        self.climate_definitions: list[TuyaClimateDefinition] = []
        self.cover_definitions: list[TuyaCoverDefinition] = []
        self.select_definitions: list[TuyaSelectDefinition] = []
        self.sensor_definitions: list[TuyaSensorDefinition] = []
        self.switch_definitions: list[TuyaSwitchDefinition] = []

        current_frame = inspect.currentframe()
        if TYPE_CHECKING:
            assert current_frame is not None
        caller = current_frame.f_back
        if TYPE_CHECKING:
            assert caller is not None
        self.quirk_file = pathlib.Path(caller.f_code.co_filename)
        self.quirk_file_line = caller.f_lineno

    def applies_to(self, *, category: str, product_id: str) -> Self:
        """Set the device type the quirk applies to."""
        self._applies_to.append((category, product_id))
        return self

    def register(self, registry: QuirksRegistry) -> None:
        """Register the quirk in the registry."""
        for category, product_id in self._applies_to:
            registry.register(category, product_id, self)

    def add_dpid_bitmap(
        self, *, dpid: int, dpcode: str, label_range: list[str]
    ) -> Self:
        """Add datapoint Bitmap definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.BITMAP,
            label_range=label_range,
        )
        return self

    def add_dpid_boolean(self, *, dpid: int, dpcode: str) -> Self:
        """Add datapoint Boolean definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.BOOLEAN,
        )
        return self

    def add_dpid_enum(
        self, *, dpid: int, dpcode: str, enum_range: list[str]
    ) -> Self:
        """Add datapoint Enum definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.ENUM,
            enum_range=enum_range,
        )
        return self

    def add_dpid_integer(
        self, *, dpid: int, dpcode: str, int_range: dict[str, Any]
    ) -> Self:
        """Add datapoint Integer definition."""
        self.datapoint_definitions[dpid] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dptype=DPType.INTEGER,
            int_range=int_range,
        )
        return self

    def add_climate(
        self,
        *,
        key: str,
        # Climate specific
        switch_only_hvac_mode: TuyaClimateHVACMode,
        current_temperature_dp_type: DeviceWrapperGenerator = _none_type_generator,
        target_temperature_dp_type: DeviceWrapperGenerator = _none_type_generator,
    ) -> Self:
        """Add climate definition."""
        self.climate_definitions.append(
            TuyaClimateDefinition(
                key=key,
                switch_only_hvac_mode=switch_only_hvac_mode,
                current_temperature_dp_type=current_temperature_dp_type,
                target_temperature_dp_type=target_temperature_dp_type,
            )
        )
        return self

    def add_cover(
        self,
        *,
        key: str,
        translation_key: str,
        translation_string: str,
        device_class: TuyaCoverDeviceClass | None = None,
        # Cover specific
        get_state_dp_type: DeviceWrapperGenerator = _none_type_generator,
        set_state_dp_type: DeviceWrapperGenerator = _none_type_generator,
        get_position_dp_type: DeviceWrapperGenerator = _none_type_generator,
        set_position_dp_type: DeviceWrapperGenerator = _none_type_generator,
    ) -> Self:
        """Add cover definition."""

        self.cover_definitions.append(
            TuyaCoverDefinition(
                key=key,
                translation_key=translation_key,
                translation_string=translation_string,
                device_class=device_class,
                get_state_dp_type=get_state_dp_type,
                set_state_dp_type=set_state_dp_type,
                get_position_dp_type=get_position_dp_type,
                set_position_dp_type=set_position_dp_type,
            )
        )
        return self

    def add_select(
        self,
        *,
        key: str,
        dp_type: DeviceWrapperGenerator | None = None,
        translation_key: str,
        translation_string: str,
        entity_category: TuyaEntityCategory | None = None,
        # Select specific
        translation_states: dict[str, str] | None = None,
    ) -> Self:
        """Add select definition."""
        if dp_type is None:
            raise NotImplementedError
        self.select_definitions.append(
            TuyaSelectDefinition(
                key=key,
                dp_type=dp_type,
                translation_key=translation_key,
                translation_string=translation_string,
                entity_category=entity_category,
                translation_states=translation_states,
            )
        )
        return self

    def add_sensor(
        self,
        *,
        key: str,
        dp_type: DeviceWrapperGenerator | None = None,
        translation_key: str | None = None,
        translation_string: str | None = None,
        device_class: TuyaSensorDeviceClass | None = None,
        entity_category: TuyaEntityCategory | None = None,
        entity_registry_enabled_default: bool = False,
        # Sensor specific
        state_class: TuyaSensorStateClass | None = None,
        suggested_unit: str | None = None,
    ) -> Self:
        """Add sensor definition."""
        if dp_type is None:
            raise NotImplementedError
        self.sensor_definitions.append(
            TuyaSensorDefinition(
                key=key,
                dp_type=dp_type,
                translation_key=translation_key,
                translation_string=translation_string,
                device_class=device_class,
                entity_category=entity_category,
                entity_registry_enabled_default=entity_registry_enabled_default,
                state_class=state_class,
                suggested_unit=suggested_unit,
            )
        )
        return self

    def add_switch(
        self,
        *,
        key: str,
        dp_type: DeviceWrapperGenerator | None = None,
        translation_key: str | None = None,
        translation_string: str | None = None,
        translation_placeholders: dict[str, str] | None = None,
        device_class: TuyaSwitchDeviceClass | None = None,
        entity_category: TuyaEntityCategory | None = None,
        # Switch specific
    ) -> Self:
        """Add switch definition."""
        if dp_type is None:
            raise NotImplementedError
        self.switch_definitions.append(
            TuyaSwitchDefinition(
                key=key,
                dp_type=dp_type,
                translation_key=translation_key,
                translation_string=translation_string,
                translation_placeholders=translation_placeholders,
                device_class=device_class,
                entity_category=entity_category,
            )
        )
        return self
