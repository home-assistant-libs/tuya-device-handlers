"""Tuya device wrapper."""

import base64
import json
import logging
from typing import TYPE_CHECKING, Any, Self

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..type_information import (
    BitmapTypeInformation,
    BooleanTypeInformation,
    EnumTypeInformation,
    IntegerTypeInformation,
    JsonTypeInformation,
    RawTypeInformation,
    StringTypeInformation,
    TypeInformation,
)
from .base import DeviceWrapper
from .const import DEVICE_WARNINGS
from .exception import SetValueOutOfRangeError

_LOGGER = logging.getLogger(__name__)


def _should_log_warning(device_id: str, warning_key: str) -> bool:
    """Check if a warning has already been logged for a device and add it if not.

    Returns: True if the warning should be logged, False if it was already logged.
    """
    if (device_warnings := DEVICE_WARNINGS.get(device_id)) is None:
        device_warnings = set()
        DEVICE_WARNINGS[device_id] = device_warnings
    if warning_key in device_warnings:
        return False
    DEVICE_WARNINGS[device_id].add(warning_key)
    return True


class DPCodeWrapper[T](DeviceWrapper[T]):
    """Base device wrapper for a single DPCode.

    Used as a common interface for referring to a DPCode, and
    access read conversion routines.
    """

    def __init__(self, dpcode: str) -> None:
        """Init DPCodeWrapper."""
        self.dpcode = dpcode

    def skip_update(
        self,
        device: CustomerDevice,
        updated_status_properties: list[str],
        dp_timestamps: dict[str, int] | None = None,
    ) -> bool:
        """Determine if the wrapper should skip an update.

        By default, skip if updated_status_properties is not given or
        does not include this dpcode.
        """
        return self.dpcode not in updated_status_properties

    def read_device_status(self, device: CustomerDevice) -> T | None:
        """Read device status and convert to a Home Assistant value."""
        return self._read_dpcode_value(device)

    def _read_dpcode_value(self, device: CustomerDevice) -> Any | None:
        """Read the DPCode value.

        Base implementation returns the raw value, subclasses may override to provide
        specific conversion or validation.
        """
        return device.status.get(self.dpcode)

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> Any:
        """Convert display value back to a raw device value.

        Base implementation does no validation, subclasses may override to provide
        specific validation.
        """
        raise NotImplementedError

    def get_update_commands(
        self, device: CustomerDevice, value: T
    ) -> list[dict[str, Any]]:
        """Get the update commands for the dpcode.

        The Home Assistant value is converted back to a raw device value.
        """
        return [
            {
                "code": self.dpcode,
                "value": self._convert_value_to_raw_value(device, value),
            }
        ]


class DPCodeTypeInformationWrapper[TypeInformationT: TypeInformation, T](
    DPCodeWrapper[T]
):
    """Base DPCode wrapper with Type Information."""

    _DPTYPE: type[TypeInformationT]
    type_information: TypeInformationT

    def __init__(self, dpcode: str, type_information: TypeInformationT) -> None:
        """Init DPCodeWrapper."""
        super().__init__(dpcode)
        self.type_information = type_information

    @classmethod
    def find_dpcode(
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        prefer_function: bool = False,
    ) -> Self | None:
        """Find and return a DPCodeTypeInformationWrapper for the given DP codes."""
        if type_information := cls._DPTYPE.find_dpcode(
            device, dpcodes, prefer_function=prefer_function
        ):
            return cls(
                dpcode=type_information.dpcode,
                type_information=type_information,
            )
        return None


class DPCodeBitmapWrapper[T = int](
    DPCodeTypeInformationWrapper[BitmapTypeInformation, T]
):
    """Simple wrapper for BitmapTypeInformation values."""

    _DPTYPE = BitmapTypeInformation

    def _read_dpcode_value(self, device: CustomerDevice) -> int | None:
        """Read and process raw value against this type information."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        if TYPE_CHECKING:
            assert isinstance(raw_value, int)
        return raw_value


class DPCodeBooleanWrapper[T = bool](
    DPCodeTypeInformationWrapper[BooleanTypeInformation, T]
):
    """Simple wrapper for BooleanTypeInformation values."""

    _DPTYPE = BooleanTypeInformation

    def _read_dpcode_value(self, device: CustomerDevice) -> bool | None:
        """Read and process raw value against this type information."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        # Validate input against defined range
        if raw_value not in (True, False):
            if _should_log_warning(
                device.id, f"boolean_out_range|{self.dpcode}|{raw_value}"
            ):
                _LOGGER.warning(
                    "Found invalid boolean value `%s` for datapoint `%s` in product "
                    "id `%s`, expected one of `%s`; please report this defect to "
                    "Tuya support",
                    raw_value,
                    self.dpcode,
                    device.product_id,
                    (True, False),
                )
            return None
        return raw_value  # type: ignore[no-any-return]

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> bool:
        """Convert a Home Assistant value back to a raw device value."""
        if value in (True, False):
            if TYPE_CHECKING:
                # mypy doesn't infer that if it's in a tuple of bools it's a bool
                assert isinstance(value, bool)
            return value
        # Currently only called with boolean values
        # Safety net in case of future changes
        raise SetValueOutOfRangeError(f"Invalid boolean value `{value}`")


class DPCodeEnumWrapper[T = str](
    DPCodeTypeInformationWrapper[EnumTypeInformation, T]
):
    """Simple wrapper for EnumTypeInformation values."""

    _DPTYPE = EnumTypeInformation
    options: list[str]

    def __init__(
        self, dpcode: str, type_information: EnumTypeInformation
    ) -> None:
        """Init DPCodeEnumWrapper."""
        super().__init__(dpcode, type_information)
        self.options = type_information.range

    def _read_dpcode_value(self, device: CustomerDevice) -> str | None:
        """Read and process raw value against this type information."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        # Validate input against defined range
        if raw_value not in self.type_information.range:
            if _should_log_warning(
                device.id, f"enum_out_range|{self.dpcode}|{raw_value}"
            ):
                _LOGGER.warning(
                    "Found invalid enum value `%s` for datapoint `%s` in product "
                    "id `%s`, expected one of `%s`; please report this defect to "
                    "Tuya support",
                    raw_value,
                    self.dpcode,
                    device.product_id,
                    self.type_information.range,
                )
            return None
        return raw_value  # type: ignore[no-any-return]

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> str:
        """Convert a Home Assistant value back to a raw device value."""
        if value in self.type_information.range:
            if TYPE_CHECKING:
                # mypy doesn't infer that if it's in a list of strings it's a string
                assert isinstance(value, str)
            return value
        # Guarded by select option validation
        # Safety net in case of future changes
        raise SetValueOutOfRangeError(
            f"Enum value `{value}` out of range: {self.type_information.range}"
        )


class DPCodeIntegerWrapper[T = float](
    DPCodeTypeInformationWrapper[IntegerTypeInformation, T]
):
    """Simple wrapper for IntegerTypeInformation values."""

    _DPTYPE = IntegerTypeInformation

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init DPCodeIntegerWrapper."""
        super().__init__(dpcode, type_information)
        self.native_unit = type_information.unit
        self.min_value = self.type_information.scale_value(type_information.min)
        self.max_value = self.type_information.scale_value(type_information.max)
        self.value_step = self.type_information.scale_value(
            type_information.step
        )

    def _read_dpcode_value(self, device: CustomerDevice) -> float | None:
        """Read and process raw value against this type information."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        # Validate input against defined range
        if not isinstance(raw_value, int) or not (
            self.type_information.min <= raw_value <= self.type_information.max
        ):
            if _should_log_warning(
                device.id, f"integer_out_range|{self.dpcode}|{raw_value}"
            ):
                _LOGGER.warning(
                    "Found invalid integer value `%s` for datapoint `%s` in product "
                    "id `%s`, expected integer value between %s and %s; please report "
                    "this defect to Tuya support",
                    raw_value,
                    self.dpcode,
                    device.product_id,
                    self.type_information.min,
                    self.type_information.max,
                )

            return None
        return self.type_information.scale_value(raw_value)

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> int:
        """Convert a Home Assistant value back to a raw device value."""
        new_value = self.type_information.scale_value_back(value)
        if self.type_information.min <= new_value <= self.type_information.max:
            return new_value
        # Guarded by number validation
        # Safety net in case of future changes
        raise SetValueOutOfRangeError(
            f"Value `{new_value}` (converted from `{value}`) out of range:"
            f" ({self.type_information.min}-{self.type_information.max})"
        )


class DPCodeJsonWrapper[T = dict[str, Any]](
    DPCodeTypeInformationWrapper[JsonTypeInformation, T]
):
    """Simple wrapper for JsonTypeInformation values."""

    _DPTYPE = JsonTypeInformation

    def _read_dpcode_value(
        self, device: CustomerDevice
    ) -> dict[str, Any] | None:
        """Read and process raw value against this type information."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        return json.loads(raw_value)  # type: ignore[no-any-return]


class DPCodeRawWrapper[T = bytes](
    DPCodeTypeInformationWrapper[RawTypeInformation, T]
):
    """Simple wrapper for RawTypeInformation values."""

    _DPTYPE = RawTypeInformation

    def _read_dpcode_value(self, device: CustomerDevice) -> bytes | None:
        """Read and process raw value against this type information."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        return base64.b64decode(raw_value)


class DPCodeStringWrapper[T = str](
    DPCodeTypeInformationWrapper[StringTypeInformation, T]
):
    """Simple wrapper for StringTypeInformation values."""

    _DPTYPE = StringTypeInformation
