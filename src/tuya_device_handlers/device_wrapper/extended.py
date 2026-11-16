"""Tuya device wrapper."""

from typing import Any, ClassVar, Self

from tuya_sharing import CustomerDevice

from tuya_device_handlers.type_information import (
    IntegerTypeInformation,
    TypeInformation,
)
from tuya_device_handlers.utils import RemapHelper

from .common import (
    DPCodeBooleanWrapper,
    DPCodeIntegerWrapper,
    DPCodeJsonWrapper,
    DPCodeTypeInformationWrapper,
)


class DPCodeRoundedIntegerWrapper(DPCodeIntegerWrapper[int]):
    """Wrapper to ensure float values are always rounded."""

    def read_device_status(self, device: CustomerDevice) -> int | None:
        """Read and round the device status."""
        if (value := super()._read_dpcode_value(device)) is None:
            return None
        return round(value)


class DPCodeRemappedIntegerWrapper(DPCodeIntegerWrapper[int]):
    """Wrapper to map Tuya integer values to a custom range."""

    _remap_helper: RemapHelper

    def __init__(
        self,
        dpcode: str,
        type_information: IntegerTypeInformation,
        *,
        target_min: int,
        target_max: int,
    ) -> None:
        """Init DPCodeRemappedIntegerWrapper."""
        super().__init__(dpcode, type_information)
        self._remap_helper = RemapHelper.from_type_information(
            type_information, target_min, target_max
        )

    def _remap_inverted(self, device: CustomerDevice) -> bool:
        """Check if the remap helper should be inverted."""
        return False

    def read_device_status(self, device: CustomerDevice) -> int | None:
        """Read and round the device status."""
        if (value := self._read_dpcode_value(device)) is None:
            return None

        return round(
            self._remap_helper.remap_value_to(
                value, reverse=self._remap_inverted(device)
            )
        )

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> int:
        return super()._convert_value_to_raw_value(
            device,
            self._remap_helper.remap_value_from(
                value, reverse=self._remap_inverted(device)
            ),
        )


class DPCodePercentageWrapper(DPCodeRemappedIntegerWrapper):
    """Wrapper to map Tuya integer values to percentage (0..100)."""

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init DPCodePercentageWrapper."""
        super().__init__(dpcode, type_information, target_min=0, target_max=100)


class DPCodeInvertedPercentageWrapper(DPCodePercentageWrapper):
    """Wrapper to map Tuya integer values to percentage (inverted 100..0)."""

    def _remap_inverted(self, device: CustomerDevice) -> bool:
        """Check if the remap helper should be inverted."""
        return True


class DPCodeInvertedBooleanWrapper(DPCodeBooleanWrapper):
    """Inverted boolean wrapper."""

    def read_device_status(self, device: CustomerDevice) -> bool | None:
        """Read the device value for this datapoint."""
        if (value := self._read_dpcode_value(device)) is None:
            return None
        return not value

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: Any
    ) -> bool:
        return not super()._convert_value_to_raw_value(device, value)


class DPCodeJsonDictAttributeWrapper[T = float](DPCodeJsonWrapper[T]):
    """Wrapper for a single attribute of a JSON dictionary value.

    The wrapper is only found if the device reports the attribute, as not
    all devices report the same set of attributes.
    """

    _ATTRIBUTE_NAME: ClassVar[str]

    @classmethod
    def find_dpcode(
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        prefer_function: bool = False,
    ) -> Self | None:
        """Find the dpcode, unless the device omits the attribute.

        The device may not have reported a status yet, in which case the
        attribute is assumed to be supported.
        """
        if (
            wrapper := super().find_dpcode(
                device, dpcodes, prefer_function=prefer_function
            )
        ) is None:
            return None
        status = wrapper._read_dpcode_value(device)  # noqa: SLF001 # pylint: disable=protected-access
        if status is None or cls._ATTRIBUTE_NAME in status:
            return wrapper
        return None

    def read_device_status(self, device: CustomerDevice) -> T | None:
        """Read the device value for the attribute."""
        if (status := self._read_dpcode_value(device)) is None:
            return None
        return status.get(self._ATTRIBUTE_NAME)


class DPCodeParsedAttributeWrapper[
    UnderlyingT,
    TypeInformationT: TypeInformation[Any],
    ParsedT,
    T = float,
](DPCodeTypeInformationWrapper[TypeInformationT, UnderlyingT, T]):
    """Wrapper for a single attribute of a parsed payload.

    The wrapper is only found if the device reports the attribute, as not
    all devices report the same set of attributes.
    """

    _ATTRIBUTE_NAME: ClassVar[str]

    @classmethod
    def _parse(cls, raw_value: UnderlyingT) -> ParsedT | None:
        """Parse the raw payload."""
        raise NotImplementedError

    @classmethod
    def find_dpcode(
        cls,
        device: CustomerDevice,
        dpcodes: str | tuple[str, ...] | None,
        *,
        prefer_function: bool = False,
    ) -> Self | None:
        """Find the dpcode, unless the device omits the attribute.

        The device may not have reported a payload yet, in which case the
        attribute is assumed to be supported. A payload which cannot be
        parsed does not provide any attribute.
        """
        if (
            wrapper := super().find_dpcode(
                device, dpcodes, prefer_function=prefer_function
            )
        ) is None:
            return None
        if not (raw_value := wrapper._read_dpcode_value(device)):  # noqa: SLF001 # pylint: disable=protected-access
            return wrapper
        if (value := cls._parse(raw_value)) is None or getattr(
            value, cls._ATTRIBUTE_NAME
        ) is None:
            return None
        return wrapper

    def read_device_status(self, device: CustomerDevice) -> T | None:
        """Read the device value for the attribute."""
        if (raw_value := self._read_dpcode_value(device)) is None or (
            value := self._parse(raw_value)
        ) is None:
            return None
        return getattr(value, self._ATTRIBUTE_NAME)
