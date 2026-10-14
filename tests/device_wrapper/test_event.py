"""Test DeviceWrapper classes."""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.event import (
    Base64Utf8RawEventWrapper,
    Base64Utf8StringEventWrapper,
    BooleanTriggerEventWrapper,
    DoorbellRingEventWrapper,
    IntegerUserIdEventWrapper,
    SimpleEventEnumWrapper,
    UnlockUserIdEventWrapper,
)


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "status", "expected_device_status"),
    [
        (
            Base64Utf8RawEventWrapper,
            "demo_raw",
            "aHR0cHM6Ly9zb21lLXBpY3R1cmUtdXJsLmNvbS9pbWFnZS5qcGc=",
            (
                "triggered",
                {"message": "https://some-picture-url.com/image.jpg"},
            ),
        ),
        (
            Base64Utf8StringEventWrapper,
            "demo_string",
            "TXkgZG9nIGF0ZSBteSBkaW5uZXI=",
            (
                "triggered",
                {"message": "My dog ate my dinner"},
            ),
        ),
        (
            SimpleEventEnumWrapper,
            "demo_enum",
            "scene",
            ("scene", None),
        ),
        (
            BooleanTriggerEventWrapper,
            "demo_boolean",
            True,
            ("triggered", None),
        ),
        (
            DoorbellRingEventWrapper,
            "demo_boolean",
            True,
            ("ring", None),
        ),
        (
            IntegerUserIdEventWrapper,
            "demo_integer",
            3,
            ("triggered", {"user_id": 3}),
        ),
        (
            UnlockUserIdEventWrapper,
            "demo_integer",
            13,
            ("unlocked", {"user_id": 13}),
        ),
    ],
)
def test_read_device_status(
    dpcode: str,
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    status: Any,
    expected_device_status: Any,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    mock_device.status[dpcode] = status
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status

    # All wrappers return None if status is None
    mock_device.status[dpcode] = None
    assert wrapper.read_device_status(mock_device) is None

    # All wrappers return None if status is missing
    mock_device.status.pop(dpcode)
    assert wrapper.read_device_status(mock_device) is None


@pytest.mark.parametrize(
    ("wrapper_type", "expected_options"),
    [
        (BooleanTriggerEventWrapper, ["triggered"]),
        (DoorbellRingEventWrapper, ["ring"]),
    ],
)
def test_boolean_trigger_event(
    wrapper_type: type[BooleanTriggerEventWrapper],
    expected_options: list[str],
    mock_device: CustomerDevice,
) -> None:
    """Test boolean trigger wrappers ignore false and expose their options."""
    wrapper = wrapper_type.find_dpcode(mock_device, "demo_boolean")

    assert wrapper
    assert wrapper.options == expected_options

    # A false report is not an event
    mock_device.status["demo_boolean"] = False
    assert wrapper.read_device_status(mock_device) is None


@pytest.mark.parametrize(
    ("wrapper_type", "expected_options"),
    [
        (IntegerUserIdEventWrapper, ["triggered"]),
        (UnlockUserIdEventWrapper, ["unlocked"]),
    ],
)
def test_integer_user_id_event_options(
    wrapper_type: type[IntegerUserIdEventWrapper],
    expected_options: list[str],
    mock_device: CustomerDevice,
) -> None:
    """Test integer user id wrappers expose their options."""
    wrapper = wrapper_type.find_dpcode(mock_device, "demo_integer")

    assert wrapper
    assert wrapper.options == expected_options
