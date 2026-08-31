"""Base quirk definition."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import inspect
import json
import pathlib
from typing import TYPE_CHECKING, Any, ClassVar, Self

from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

from tuya_device_handlers.const import DPMode, DPType
from tuya_device_handlers.device_wrapper.base import DeviceWrapper
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    FeederSchedule,
)
from tuya_device_handlers.registry import DeviceQuirkProtocol, QuirksRegistry
from tuya_device_handlers.type_information import TypeInformation


@dataclass(kw_only=True)
class _QuirkEntry(ABC):
    """Base for an entry that a quirk applies to a device.

    When `apply_when` is set, the entry is only applied to devices for
    which the callable returns True. This allows a quirk to cover
    variants that share a product_id but behave differently.

    Subclasses that only make sense for locally controlled devices set
    `requires_local_support`, which skips them when the device does not
    support local control.
    """

    requires_local_support: ClassVar[bool] = False

    dpid: int
    dpcode: str
    apply_when: Callable[[CustomerDevice], bool] | None = None

    def applies_to_device(self, device: CustomerDevice) -> bool:
        """Check whether this entry applies to the device."""
        if self.requires_local_support and not device.support_local:
            return False
        return self.apply_when is None or self.apply_when(device)

    @abstractmethod
    def apply(self, device: CustomerDevice) -> None:
        """Apply this entry to the device."""


@dataclass(kw_only=True)
class _LocalConvertStrategy(_QuirkEntry):
    """Definition for a local convert strategy."""

    requires_local_support: ClassVar[bool] = True

    value_convert: str
    enum_mapping_map: dict[str, dict[str, Any]] | None = None

    def apply(self, device: CustomerDevice) -> None:
        """Set the local strategy on the device."""
        device.local_strategy[self.dpid] = self.to_local_strategy(
            device.product_id,
            device.status_range.get(self.dpcode),
        )

    def to_local_strategy(
        self, product_id: str, status_range: DeviceStatusRange | None
    ) -> dict[str, Any]:
        """Convert to LocalStrategy."""
        return {
            "value_convert": self.value_convert,
            "status_code": self.dpcode,
            "config_item": {
                "statusFormat": json.dumps({self.dpcode: "$"}),
                "valueDesc": status_range.values if status_range else "",
                "valueType": status_range.type if status_range else "",
                "enumMappingMap": self.enum_mapping_map or {},
                "pid": product_id,
            },
        }


@dataclass(kw_only=True)
class _LocalStrategyRemoval(_QuirkEntry):
    """Removal of a local convert strategy."""

    requires_local_support: ClassVar[bool] = True

    def apply(self, device: CustomerDevice) -> None:
        """Remove the local strategy from the device."""
        device.local_strategy.pop(self.dpid, None)


@dataclass(kw_only=True)
class _DatapointRemoval(_QuirkEntry):
    """Removal of a Tuya datapoint."""

    def apply(self, device: CustomerDevice) -> None:
        """Remove the datapoint from the device."""
        device.function.pop(self.dpcode, None)
        device.local_strategy.pop(self.dpid, None)
        device.status.pop(self.dpcode, None)
        device.status_range.pop(self.dpcode, None)


@dataclass(kw_only=True)
class _InitialStatusValueMapping(_QuirkEntry):
    """Mapping applied to the initial status value of a datapoint.

    The cloud may report the cached status of a datapoint in a different
    shape than the values reported later over MQTT (for example the
    strings ``"true"``/``"false"`` for a Boolean datapoint). This entry
    rewrites the initial value so it matches the expected type.
    """

    status_mapping: dict[Any, Any]

    def apply(self, device: CustomerDevice) -> None:
        """Map the initial status value on the device."""
        raw_value = device.status.get(self.dpcode)
        try:
            if raw_value in self.status_mapping:
                device.status[self.dpcode] = self.status_mapping[raw_value]
        except TypeError:  # unhashable raw value
            pass


@dataclass(kw_only=True)
class _DatapointDefinition(_QuirkEntry):
    """Definition for a Tuya datapoint."""

    dpmode: DPMode
    dptype: DPType
    values: str | None = None
    report_type: str | None = None

    def apply(self, device: CustomerDevice) -> None:
        """Add or update the datapoint on the device."""
        if DPMode.READ in self.dpmode:
            device.status_range[self.dpcode] = self.to_status_range()
        else:
            device.status_range.pop(self.dpcode, None)

        if DPMode.WRITE in self.dpmode:
            device.function[self.dpcode] = self.to_function()
        else:
            device.function.pop(self.dpcode, None)

        if device.support_local:
            device.local_strategy[self.dpid] = self.to_local_strategy(
                device.product_id
            )
        else:
            device.local_strategy.pop(self.dpid, None)

    def to_function(self) -> DeviceFunction:
        """Convert to DeviceFunction."""
        return DeviceFunction(
            code=self.dpcode,
            type=self.dptype.value,
            values=self.values,
        )

    def to_local_strategy(self, product_id: str) -> dict[str, Any]:
        """Convert to LocalStrategy."""
        return {
            "value_convert": "default",
            "status_code": self.dpcode,
            "config_item": {
                "statusFormat": json.dumps({self.dpcode: "$"}),
                "valueDesc": self.values,
                "valueType": self.dptype.value,
                "enumMappingMap": {},
                "pid": product_id,
            },
        }

    def to_status_range(self) -> DeviceStatusRange:
        """Convert to DeviceStatusRange."""
        return DeviceStatusRange(
            code=self.dpcode,
            type=self.dptype.value,
            values=self.values,
            report_type=self.report_type,
        )


class DeviceQuirk(DeviceQuirkProtocol):
    """Quirk for Tuya device."""

    _quirk_entries: list[_QuirkEntry]
    _type_information_overrides: dict[
        tuple[int, str], type[TypeInformation[Any]]
    ]
    _get_wrapper_functions: dict[
        str,
        Callable[[CustomerDevice], DeviceWrapper | None],
    ]

    def __init__(self) -> None:
        """Initialize the quirk."""
        self._applies_to: str | None = None
        self._override_category: str | None = None

        self._quirk_entries = []
        self._type_information_overrides = {}
        self._get_wrapper_functions = {}

        current_frame = inspect.currentframe()
        if TYPE_CHECKING:
            assert current_frame is not None
        caller = current_frame.f_back
        if TYPE_CHECKING:
            assert caller is not None
        self._quirk_file = pathlib.Path(caller.f_code.co_filename)
        self._quirk_file_line = caller.f_lineno

    @property
    def quirk_file(self) -> pathlib.Path:
        """Get the file path of the quirk."""
        return self._quirk_file

    @property
    def quirk_file_line(self) -> int:
        """Get the line number of the quirk."""
        return self._quirk_file_line

    def initialise_device(self, device: CustomerDevice) -> None:
        """Initialise device."""
        self.original_category = device.category
        self.original_function = device.function.copy()
        self.original_local_strategy = device.local_strategy.copy()
        self.original_status_range = device.status_range.copy()

        if self._override_category is not None:
            device.category = self._override_category

        # Entries are applied in the order the builder methods were called.
        # A _LocalConvertStrategy reads device.status_range, so it must be
        # added after the datapoint definition that provides its dpcode.
        for entry in self._quirk_entries:
            if entry.applies_to_device(device):
                entry.apply(device)

    def applies_to(
        self,
        *,
        product_id: str,
        manufacturer: str | None = None,
        model: str | None = None,
        model_id: str | None = None,
    ) -> Self:
        """Set the device type the quirk applies to."""
        if self._applies_to is not None:
            msg = "DeviceQuirk already has an applies_to condition"
            raise ValueError(msg)
        self._applies_to = product_id
        self.manufacturer = manufacturer
        self.model = model
        self.model_id = model_id
        return self

    def override_category(self, category: str) -> Self:
        """Set category override applied during initialise_device."""
        self._override_category = category
        return self

    def register(self, registry: QuirksRegistry) -> None:
        """Register the quirk in the registry."""
        if self._applies_to is None:
            msg = "DeviceQuirk does not have an applies_to condition"
            raise ValueError(msg)
        registry.register(self._applies_to, self)

    def add_dpid_bitmap(
        self,
        *,
        dpid: int,
        dpcode: str,
        dpmode: DPMode,
        label_range: list[str],
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Add datapoint Bitmap definition."""
        self._quirk_entries.append(
            _DatapointDefinition(
                dpid=dpid,
                dpcode=dpcode,
                dpmode=dpmode,
                dptype=DPType.BITMAP,
                values=json.dumps({"label": label_range}),
                apply_when=apply_when,
            )
        )
        return self

    def add_dpid_boolean(
        self,
        *,
        dpid: int,
        dpcode: str,
        dpmode: DPMode,
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Add datapoint Boolean definition."""
        self._quirk_entries.append(
            _DatapointDefinition(
                dpid=dpid,
                dpcode=dpcode,
                dpmode=dpmode,
                dptype=DPType.BOOLEAN,
                values="{}",
                apply_when=apply_when,
            )
        )
        return self

    def add_dpid_enum(
        self,
        *,
        dpid: int,
        dpcode: str,
        dpmode: DPMode,
        enum_range: list[str],
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Add datapoint Enum definition."""
        self._quirk_entries.append(
            _DatapointDefinition(
                dpid=dpid,
                dpcode=dpcode,
                dpmode=dpmode,
                dptype=DPType.ENUM,
                values=json.dumps({"range": enum_range}),
                apply_when=apply_when,
            )
        )
        return self

    def add_dpid_integer(
        self,
        *,
        dpid: int,
        dpcode: str,
        dpmode: DPMode,
        unit: str,
        min: int,  # noqa: A002  # pylint: disable=redefined-builtin
        max: int,  # noqa: A002  # pylint: disable=redefined-builtin
        scale: int,
        step: int,
        report_type: str | None = None,
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Add datapoint Integer definition."""
        self._quirk_entries.append(
            _DatapointDefinition(
                dpid=dpid,
                dpcode=dpcode,
                dpmode=dpmode,
                dptype=DPType.INTEGER,
                report_type=report_type,
                values=json.dumps(
                    {
                        "unit": unit,
                        "min": min,
                        "max": max,
                        "scale": scale,
                        "step": step,
                    }
                ),
                apply_when=apply_when,
            )
        )
        return self

    def map_dpid_initial_status_values(
        self,
        *,
        dpid: int,
        dpcode: str,
        status_mapping: dict[Any, Any],
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Map the initial status value of a datapoint."""
        self._quirk_entries.append(
            _InitialStatusValueMapping(
                dpid=dpid,
                dpcode=dpcode,
                status_mapping=status_mapping,
                apply_when=apply_when,
            )
        )
        return self

    def override_dpid_type_information_cls(
        self,
        *,
        dpid: int,
        dpcode: str,
        type_information_cls: type[TypeInformation[Any]],
    ) -> Self:
        """Override the TypeInformation class used for a datapoint."""
        self._type_information_overrides[(dpid, dpcode)] = type_information_cls
        return self

    def remove_dpid(
        self,
        *,
        dpid: int,
        dpcode: str,
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Remove datapoint definition."""
        self._quirk_entries.append(
            _DatapointRemoval(dpid=dpid, dpcode=dpcode, apply_when=apply_when)
        )
        return self

    def set_dpid_strategy_to_enum(
        self,
        *,
        dpid: int,
        dpcode: str,
        enum_mapping_map: dict[Any, Any],
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Override local strategy for a datapoint."""
        self._quirk_entries.append(
            _LocalConvertStrategy(
                dpid=dpid,
                dpcode=dpcode,
                value_convert="enum",
                enum_mapping_map={
                    str(key): {"value": value}
                    for key, value in enum_mapping_map.items()
                },
                apply_when=apply_when,
            )
        )
        return self

    def remove_dpid_strategy(
        self,
        *,
        dpid: int,
        dpcode: str,
        apply_when: Callable[[CustomerDevice], bool] | None = None,
    ) -> Self:
        """Remove datapoint strategy."""
        self._quirk_entries.append(
            _LocalStrategyRemoval(
                dpid=dpid, dpcode=dpcode, apply_when=apply_when
            )
        )
        return self

    def map_feeder_schedules_wrapper(
        self,
        *,
        wrapper_function: Callable[
            [CustomerDevice], DeviceWrapper[list[FeederSchedule]] | None
        ],
    ) -> Self:
        """Map feeder schedule service."""
        self._get_wrapper_functions["feeder_schedules"] = wrapper_function
        return self

    def get_feeder_schedules_wrapper(
        self, device: CustomerDevice
    ) -> DeviceWrapper[list[FeederSchedule]] | None:
        """Get the feeder schedules wrapper for a device."""
        if get_wrapper_function := self._get_wrapper_functions.get(
            "feeder_schedules"
        ):
            return get_wrapper_function(device)

        return None

    def get_type_information_cls(
        self, *, dpcode: str
    ) -> type[TypeInformation[Any]] | None:
        """Get the type information class override for a dpcode."""
        for (_, code), type_cls in self._type_information_overrides.items():
            if code == dpcode:
                return type_cls
        return None
