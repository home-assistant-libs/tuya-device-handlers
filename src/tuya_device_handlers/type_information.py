"""Type information classes for the Tuya integration."""

import abc
import base64
import binascii
from dataclasses import dataclass
import json
import logging
from typing import Any, ClassVar, Self, cast

from tuya_sharing import CustomerDevice

from .const import DEVICE_WARNINGS, DPType

_LOGGER = logging.getLogger(__name__)

_LOG_OR_QUIRK = (
    "please report this defect to Tuya support, or create a quirk "
    "at https://github.com/home-assistant-libs/tuya-device-handlers"
)


def _should_log_warning(device_id: str, warning_key: str) -> bool:
    """Check if a warning was already logged for a device.

    Returns: True if the warning should be logged,
    False if it was already logged.
    """
    if (device_warnings := DEVICE_WARNINGS.get(device_id)) is None:
        device_warnings = set()
        DEVICE_WARNINGS[device_id] = device_warnings
    if warning_key in device_warnings:
        return False
    DEVICE_WARNINGS[device_id].add(warning_key)
    return True


@dataclass(kw_only=True)
class TypeInformation[T](abc.ABC):
    """Type information.

    As provided by the SDK, from `device.function` / `device.status_range`.
    """

    _DPTYPE: ClassVar[DPType]
    dpcode: str
    type_data: str
    report_type: str | None

    @classmethod
    def _from_json(
        cls,
        dpcode: str,
        type_data: str,
        *,
        report_type: str | None,
    ) -> Self | None:
        """Load JSON string and return a TypeInformation object."""
        return cls(dpcode=dpcode, type_data=type_data, report_type=report_type)

    @classmethod
    def find_dpcode(
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        prefer_function: bool = False,
    ) -> Self | None:
        """Find type information for a matching DP code."""
        return get_type_information(
            device,
            dpcodes,
            prefer_function=prefer_function,
            type_information_cls=cls,
        )

    @abc.abstractmethod
    def read_device_value(self, device: CustomerDevice) -> T | None:
        """Read (and validate + convert) device value."""


@dataclass(kw_only=True)
class BitmapTypeInformation(TypeInformation[int]):
    """Bitmap type information."""

    _DPTYPE = DPType.BITMAP

    label: list[str]

    @classmethod
    def _from_json(
        cls,
        dpcode: str,
        type_data: str,
        *,
        report_type: str | None,
    ) -> Self | None:
        """Load JSON string and return a BitmapTypeInformation object."""
        if not (parsed := cast(dict[str, Any] | None, json.loads(type_data))):
            return None
        return cls(
            dpcode=dpcode,
            type_data=type_data,
            report_type=report_type,
            label=parsed["label"],
        )

    def read_device_value(self, device: CustomerDevice) -> int | None:
        """Read the device value for this datapoint."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        if isinstance(raw_value, int):
            return raw_value
        if _should_log_warning(
            device.id, f"invalid_bitmap|{self.dpcode}|{raw_value}"
        ):
            _LOGGER.warning(
                "Found invalid BITMAP value `%s` (%s) for datapoint `%s` in "
                "product id `%s`; %s",
                raw_value,
                type(raw_value),
                self.dpcode,
                device.product_id,
                _LOG_OR_QUIRK,
            )
        return None


@dataclass(kw_only=True)
class BooleanTypeInformation(TypeInformation[bool]):
    """Boolean type information."""

    _DPTYPE = DPType.BOOLEAN

    def read_device_value(self, device: CustomerDevice) -> bool | None:
        """Read the device value for this datapoint."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        if raw_value in (True, False):
            return cast(bool, raw_value)

        if _should_log_warning(
            device.id, f"boolean_out_range|{self.dpcode}|{raw_value}"
        ):
            _LOGGER.warning(
                "Found invalid BOOLEAN value `%s` (%s) for datapoint `%s` in "
                "product id `%s`; %s",
                raw_value,
                type(raw_value),
                self.dpcode,
                device.product_id,
                _LOG_OR_QUIRK,
            )
        return None


@dataclass(kw_only=True)
class EnumTypeInformation(TypeInformation[str]):
    """Enum type information."""

    _DPTYPE = DPType.ENUM

    range: list[str]

    @classmethod
    def _from_json(
        cls,
        dpcode: str,
        type_data: str,
        *,
        report_type: str | None,
    ) -> Self | None:
        """Load JSON string and return an EnumTypeInformation object."""
        if not (parsed := json.loads(type_data)):
            return None
        return cls(
            dpcode=dpcode,
            type_data=type_data,
            report_type=report_type,
            **cast(dict[str, list[str]], parsed),
        )

    def read_device_value(self, device: CustomerDevice) -> str | None:
        """Read the device value for this datapoint."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        # Validate input against defined range
        if raw_value in self.range:
            return cast(str, raw_value)

        if _should_log_warning(
            device.id, f"enum_out_range|{self.dpcode}|{raw_value}"
        ):
            _LOGGER.warning(
                "Found invalid ENUM value `%s` (%s) for datapoint `%s` in "
                "product id `%s`, expected one of `%s`; %s",
                raw_value,
                type(raw_value),
                self.dpcode,
                device.product_id,
                self.range,
                _LOG_OR_QUIRK,
            )
        return None


@dataclass(kw_only=True)
class IntegerTypeInformation(TypeInformation[float]):
    """Integer type information."""

    _DPTYPE = DPType.INTEGER

    min: int
    max: int
    scale: int
    step: int
    unit: str | None = None

    def scale_value(self, value: int) -> float:
        """Scale a value."""
        return value / (10**self.scale)

    def scale_value_back(self, value: float) -> int:
        """Return raw value for scaled."""
        return round(value * (10**self.scale))

    @classmethod
    def _from_json(
        cls, dpcode: str, type_data: str, *, report_type: str | None
    ) -> Self | None:
        """Load JSON string and return an IntegerTypeInformation object."""
        if not (parsed := cast(dict[str, Any] | None, json.loads(type_data))):
            return None

        return cls(
            dpcode=dpcode,
            type_data=type_data,
            min=int(parsed["min"]),
            max=int(parsed["max"]),
            scale=int(parsed["scale"]),
            step=int(parsed["step"]),
            unit=parsed.get("unit"),
            report_type=report_type,
        )

    def read_device_value(self, device: CustomerDevice) -> float | None:
        """Read the device value for this datapoint."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        # Validate input against defined range
        if isinstance(raw_value, int) and (self.min <= raw_value <= self.max):
            return self.scale_value(raw_value)
        if _should_log_warning(
            device.id, f"integer_out_range|{self.dpcode}|{raw_value}"
        ):
            _LOGGER.warning(
                "Found invalid INTEGER value `%s` (%s) for datapoint `%s` in "
                "product id `%s`, expected value between %s and %s; %s",
                raw_value,
                type(raw_value),
                self.dpcode,
                device.product_id,
                self.min,
                self.max,
                _LOG_OR_QUIRK,
            )

        return None


@dataclass(kw_only=True)
class JsonTypeInformation(TypeInformation[dict[str, Any]]):
    """Json type information."""

    _DPTYPE = DPType.JSON

    def read_device_value(
        self, device: CustomerDevice
    ) -> dict[str, Any] | None:
        """Read the device value for this datapoint."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        try:
            return cast(dict[str, Any], json.loads(raw_value))
        except json.JSONDecodeError:
            if _should_log_warning(device.id, f"invalid_json|{self.dpcode}"):
                _LOGGER.warning(
                    "Found invalid JSON value `%s` (%s) for datapoint `%s` in "
                    "product id `%s`; %s",
                    raw_value,
                    type(raw_value),
                    self.dpcode,
                    device.product_id,
                    _LOG_OR_QUIRK,
                )
        return None


@dataclass(kw_only=True)
class RawTypeInformation(TypeInformation[bytes]):
    """Raw type information."""

    _DPTYPE = DPType.RAW

    def read_device_value(self, device: CustomerDevice) -> bytes | None:
        """Read the device value for this datapoint."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        try:
            return base64.b64decode(raw_value)
        except (binascii.Error, TypeError):
            if _should_log_warning(device.id, f"invalid_raw|{self.dpcode}"):
                _LOGGER.warning(
                    "Found invalid RAW value `%s` (%s) for datapoint `%s` in "
                    "product id `%s`; %s",
                    raw_value,
                    type(raw_value),
                    self.dpcode,
                    device.product_id,
                    _LOG_OR_QUIRK,
                )
        return None


@dataclass(kw_only=True)
class StringTypeInformation(TypeInformation[str]):
    """String type information."""

    _DPTYPE = DPType.STRING

    def read_device_value(self, device: CustomerDevice) -> str | None:
        """Read the device value for this datapoint."""
        return cast(str, device.status.get(self.dpcode))


def get_type_information[T: TypeInformation](
    device: CustomerDevice,
    dpcodes: str | tuple[str, ...] | None,
    *,
    prefer_function: bool = False,
    type_information_cls: type[T],
) -> T | None:
    """Find type information for a device DP code."""
    if dpcodes is None:
        return None

    if not isinstance(dpcodes, tuple):
        dpcodes = (dpcodes,)

    for dpcode in dpcodes:
        if type_information := _get_device_dpcode_type_information(
            device=device,
            dpcode=dpcode,
            prefer_function=prefer_function,
            type_information_cls=type_information_cls,
        ):
            return type_information

    return None


def _get_device_dpcode_type_information[T: TypeInformation](
    device: CustomerDevice,
    dpcode: str,
    *,
    prefer_function: bool = False,
    type_information_cls: type[T],
) -> T | None:
    """Find type information for a device DP code."""
    # Get definitions
    function_definition = device.function.get(dpcode)
    status_range_definition = device.status_range.get(dpcode)

    # Validate definitions against expected DP type, ignore if not matching
    # pylint: disable-next=protected-access
    dp_type = type_information_cls._DPTYPE  # noqa: SLF001
    if (
        function_definition
        and DPType.try_parse(function_definition.type) is not dp_type
    ):
        function_definition = None

    if (
        status_range_definition
        and DPType.try_parse(status_range_definition.type) is not dp_type
    ):
        status_range_definition = None

    # report_type is not available on function definitions
    report_type = (
        status_range_definition.report_type if status_range_definition else None
    )

    # Get type_information based on definition preference
    lookup = (
        (function_definition, status_range_definition)
        if prefer_function
        else (status_range_definition, function_definition)
    )
    for definition in lookup:
        if definition is not None and (
            # pylint: disable-next=protected-access
            type_information := type_information_cls._from_json(  # noqa: SLF001
                dpcode=dpcode,
                type_data=definition.values,
                report_type=report_type,
            )
        ):
            return type_information

    return None
