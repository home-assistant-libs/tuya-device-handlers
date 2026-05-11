"""Base quirk definition."""

from collections.abc import Callable
from dataclasses import dataclass
import inspect
import json
import pathlib
from typing import TYPE_CHECKING, Any, Self

from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

from tuya_device_handlers.const import DPMode, DPType
from tuya_device_handlers.device_wrapper.base import DeviceWrapper
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    FeederSchedule,
)
from tuya_device_handlers.registry import DeviceQuirkProtocol, QuirksRegistry


@dataclass(kw_only=True)
class DatapointDefinition:
    """Definition for a Tuya datapoint."""

    dpid: int
    dpcode: str
    dpmode: DPMode
    dptype: DPType
    values: str | None = None
    report_type: str | None = None

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
        )


class DeviceQuirk(DeviceQuirkProtocol):
    """Quirk for Tuya device."""

    _datapoint_definitions: dict[tuple[int, str], DatapointDefinition | None]
    _get_wrapper_functions: dict[
        str,
        Callable[[CustomerDevice], DeviceWrapper | None],
    ]

    def __init__(self) -> None:
        """Initialize the quirk."""
        self._applies_to: str | None = None

        self._datapoint_definitions = {}
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
        self.original_function = device.function.copy()
        self.original_local_strategy = device.local_strategy.copy()
        self.original_status_range = device.status_range.copy()

        for key, definition in self._datapoint_definitions.items():
            dpid, dpcode = key

            # Remove definition if explicit None
            if definition is None:
                device.function.pop(dpcode, None)
                device.local_strategy.pop(dpid, None)
                device.status.pop(dpcode, None)
                device.status_range.pop(dpcode, None)
                continue

            # Add or remove function/status_range attributes
            if DPMode.READ in definition.dpmode:
                device.status_range[definition.dpcode] = (
                    definition.to_status_range()
                )
            else:
                device.status_range.pop(definition.dpcode, None)

            if DPMode.WRITE in definition.dpmode:
                device.function[definition.dpcode] = definition.to_function()
            else:
                device.function.pop(definition.dpcode, None)

            if device.support_local:
                device.local_strategy[definition.dpid] = (
                    definition.to_local_strategy(device.product_id)
                )
            else:
                device.local_strategy.pop(definition.dpid, None)

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

    def register(self, registry: QuirksRegistry) -> None:
        """Register the quirk in the registry."""
        if self._applies_to is None:
            msg = "DeviceQuirk does not have an applies_to condition"
            raise ValueError(msg)
        registry.register(self._applies_to, self)

    def add_dpid_bitmap(
        self, *, dpid: int, dpcode: str, dpmode: DPMode, label_range: list[str]
    ) -> Self:
        """Add datapoint Bitmap definition."""
        self._datapoint_definitions[(dpid, dpcode)] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dpmode=dpmode,
            dptype=DPType.BITMAP,
            values=json.dumps({"label": label_range}),
        )
        return self

    def add_dpid_boolean(
        self, *, dpid: int, dpcode: str, dpmode: DPMode
    ) -> Self:
        """Add datapoint Boolean definition."""
        self._datapoint_definitions[(dpid, dpcode)] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dpmode=dpmode,
            dptype=DPType.BOOLEAN,
            values="{}",
        )
        return self

    def add_dpid_enum(
        self, *, dpid: int, dpcode: str, dpmode: DPMode, enum_range: list[str]
    ) -> Self:
        """Add datapoint Enum definition."""
        self._datapoint_definitions[(dpid, dpcode)] = DatapointDefinition(
            dpid=dpid,
            dpcode=dpcode,
            dpmode=dpmode,
            dptype=DPType.ENUM,
            values=json.dumps({"range": enum_range}),
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
    ) -> Self:
        """Add datapoint Integer definition."""
        self._datapoint_definitions[(dpid, dpcode)] = DatapointDefinition(
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
        )
        return self

    def remove_dpid(self, *, dpid: int, dpcode: str) -> Self:
        """Remove datapoint definition."""
        self._datapoint_definitions[(dpid, dpcode)] = None
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
