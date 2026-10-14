"""Tuya device wrapper."""

import base64
from typing import Any

from tuya_sharing import CustomerDevice

from .common import (
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
    DPCodeRawWrapper,
    DPCodeStringWrapper,
)


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


class BooleanTriggerEventWrapper(DPCodeBooleanWrapper[tuple[str, None]]):
    """Wrapper for Boolean DP codes pushed as true when something happens.

    Locks report e.g. `doorbell: true` or `hijack: true` and never reset the
    value, so a binary sensor would stay on forever. Raises a 'triggered'
    event whenever the DP code is reported as true; false is ignored.
    """

    _EVENT_TYPE = "triggered"

    def __init__(self, dpcode: str, type_information: Any) -> None:
        """Init BooleanTriggerEventWrapper."""
        super().__init__(dpcode, type_information)
        self.options = [self._EVENT_TYPE]

    def read_device_status(
        self, device: CustomerDevice
    ) -> tuple[str, None] | None:
        """Return the event when the DP code is true."""
        if not self._read_dpcode_value(device):
            return None
        return (self._EVENT_TYPE, None)


class DoorbellRingEventWrapper(BooleanTriggerEventWrapper):
    """Boolean trigger raising the 'ring' event of the doorbell device class."""

    _EVENT_TYPE = "ring"


class IntegerUserIdEventWrapper(
    DPCodeIntegerWrapper[tuple[str, dict[str, Any]]]
):
    """Wrapper for Integer DP codes reporting an action with a user id.

    Locks report e.g. `unlock_fingerprint: 3` every time user 3 unlocks the
    door. Raises a 'triggered' event with the user id in the attributes.
    """

    _EVENT_TYPE = "triggered"

    def __init__(self, dpcode: str, type_information: Any) -> None:
        """Init IntegerUserIdEventWrapper."""
        super().__init__(dpcode, type_information)
        self.options = [self._EVENT_TYPE]

    def read_device_status(
        self, device: CustomerDevice
    ) -> tuple[str, dict[str, Any]] | None:
        """Return the event with the user id attribute."""
        if (raw_value := device.status.get(self.dpcode)) is None:
            return None
        return (self._EVENT_TYPE, {"user_id": int(raw_value)})


class UnlockUserIdEventWrapper(IntegerUserIdEventWrapper):
    """Integer user id wrapper raising an 'unlocked' event (lock unlock DPs)."""

    _EVENT_TYPE = "unlocked"
