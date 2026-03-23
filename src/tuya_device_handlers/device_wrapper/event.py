"""Tuya device wrapper."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .base import DeviceWrapper
from .common import DPCodeEnumWrapper, DPCodeRawWrapper, DPCodeStringWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


@dataclass
class TuyaEventDefinition:
    event_wrapper: DeviceWrapper[tuple[str, dict[str, Any] | None]]


class SimpleEventEnumWrapper(DPCodeEnumWrapper[tuple[str, None]]):
    """Wrapper for event enum DP codes.

    Does not provide attributes.
    """

    def read_device_status(
        self, device: CustomerDevice
    ) -> tuple[str, None] | None:
        """Return the event details."""
        if (raw_value := self._read_dpcode_value(device)) is None:
            return None
        return (raw_value, None)


class Base64Utf8StringEventWrapper(
    DPCodeStringWrapper[tuple[str, dict[str, Any]]]
):
    """Wrapper for a string message received in a base64/UTF-8 STRING DPCode.

    Raises 'triggered' event, with the message in the event attributes.
    """

    def __init__(self, dpcode: str, type_information: Any) -> None:
        """Init Base64Utf8StringEventWrapper."""
        super().__init__(dpcode, type_information)
        self.options = ["triggered"]

    def read_device_status(
        self, device: CustomerDevice
    ) -> tuple[str, dict[str, Any]] | None:
        """Return the event with message attribute."""
        if (raw_value := self._read_dpcode_value(device)) is None:
            return None
        return (
            "triggered",
            {"message": base64.b64decode(raw_value).decode("utf-8")},
        )


class Base64Utf8RawEventWrapper(DPCodeRawWrapper[tuple[str, dict[str, Any]]]):
    """Wrapper for a string message received in a base64/UTF-8 RAW DPCode.

    Raises 'triggered' event, with the message in the event attributes.
    """

    def __init__(self, dpcode: str, type_information: Any) -> None:
        """Init Base64Utf8RawEventWrapper."""
        super().__init__(dpcode, type_information)
        self.options = ["triggered"]

    def read_device_status(
        self, device: CustomerDevice
    ) -> tuple[str, dict[str, Any]] | None:
        """Return the event with message attribute."""
        if (status := self._read_dpcode_value(device)) is None:
            return None
        return ("triggered", {"message": status.decode("utf-8")})
