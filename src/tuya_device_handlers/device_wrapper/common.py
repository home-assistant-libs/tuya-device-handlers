"""Tuya device wrapper."""

from typing import Any, Self

from tuya_sharing import CustomerDevice

from tuya_device_handlers.type_information import (
    BitmapTypeInformation,
    BooleanTypeInformation,
    EnumTypeInformation,
    IntegerTypeInformation,
    JsonTypeInformation,
    PrepareSetValueError,
    RawTypeInformation,
    StringTypeInformation,
    TypeInformation,
)

from .base import DeviceWrapper
from .exception import SetValueOutOfRangeError


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

        Base implementation returns the raw value, subclasses
        may override to provide specific conversion or
        validation.
        """
        return device.status.get(self.dpcode)

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> Any:
        """Convert display value back to a raw device value.

        Base implementation does no validation, subclasses may
        override to provide specific validation.
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


class DPCodeTypeInformationWrapper[
    TypeInformationT: TypeInformation[Any],
    UnderlyingT,
    T,
](DPCodeWrapper[T]):
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
        """Find a DPCodeTypeInformationWrapper for the given DP codes."""
        if type_information := cls._DPTYPE.find_dpcode(
            device, dpcodes, prefer_function=prefer_function
        ):
            return cls(
                dpcode=type_information.dpcode,
                type_information=type_information,
            )
        return None

    def _read_dpcode_value(self, device: CustomerDevice) -> UnderlyingT | None:
        """Read and process raw value against this type information."""
        return self.type_information.read_device_value(device)

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> Any:
        """Convert a Home Assistant value back to a raw device value."""
        try:
            return self.type_information.prepare_set_value(device, value)
        except PrepareSetValueError as err:
            raise SetValueOutOfRangeError(str(err)) from err


class DPCodeBitmapWrapper[T = int](
    DPCodeTypeInformationWrapper[BitmapTypeInformation, int, T]
):
    """Simple wrapper for BitmapTypeInformation values."""

    _DPTYPE = BitmapTypeInformation


class DPCodeBooleanWrapper[T = bool](
    DPCodeTypeInformationWrapper[BooleanTypeInformation, bool, T]
):
    """Simple wrapper for BooleanTypeInformation values."""

    _DPTYPE = BooleanTypeInformation


class DPCodeEnumWrapper[T = str](
    DPCodeTypeInformationWrapper[EnumTypeInformation, str, T]
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


class DPCodeIntegerWrapper[T = float](
    DPCodeTypeInformationWrapper[IntegerTypeInformation, float, T]
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


class DPCodeJsonWrapper[T = dict[str, Any]](
    DPCodeTypeInformationWrapper[JsonTypeInformation, dict[str, Any], T]
):
    """Simple wrapper for JsonTypeInformation values."""

    _DPTYPE = JsonTypeInformation


class DPCodeRawWrapper[T = bytes](
    DPCodeTypeInformationWrapper[RawTypeInformation, bytes, T]
):
    """Simple wrapper for RawTypeInformation values."""

    _DPTYPE = RawTypeInformation


class DPCodeStringWrapper[T = str](
    DPCodeTypeInformationWrapper[StringTypeInformation, str, T]
):
    """Simple wrapper for StringTypeInformation values."""

    _DPTYPE = StringTypeInformation
