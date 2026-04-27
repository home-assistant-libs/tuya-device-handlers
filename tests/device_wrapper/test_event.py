"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.event import (
    Base64Utf8RawEventWrapper,
    Base64Utf8StringEventWrapper,
    SimpleEventEnumWrapper,
)

try:
    from typeguard import suppress_type_checks  # type: ignore[import-not-found]
except ImportError:
    from contextlib import nullcontext

    suppress_type_checks = nullcontext


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
