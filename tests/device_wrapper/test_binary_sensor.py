"""Test DeviceWrapper classes"""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper.binary_sensor import (
    DPCodeBitmapBitWrapper,
    DPCodeInSetWrapper,
)


@pytest.mark.parametrize(
    ("dpcode", "bitmap_key"),
    [
        ("invalid", "invalid"),
        ("demo_bitmap", "invalid"),
    ],
)
def test_bitmapbit_dpcode_not_found(
    mock_device: CustomerDevice, dpcode: str, bitmap_key: str
) -> None:
    """Test find_dpcode with invalid dpcode."""
    type_information = DPCodeBitmapBitWrapper.find_dpcode(
        mock_device, dpcode, bitmap_key=bitmap_key
    )

    assert type_information is None


@pytest.mark.parametrize(
    ("status", "expected_device_status"),
    [
        (None, None),
        (0, False),
        (1, True),
        (2, False),
        (3, True),
    ],
)
def test_bitmapbit_device_status(
    status: Any | None,
    expected_device_status: Any | None,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    mock_device.status["demo_bitmap"] = status
    wrapper = DPCodeBitmapBitWrapper.find_dpcode(
        mock_device, "demo_bitmap", bitmap_key="motor_fault"
    )

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status


@pytest.mark.parametrize(
    ("status", "expected_device_status"),
    [
        (None, None),
        ("alarm", True),
        ("normal", False),
    ],
)
def test_inset_device_status(
    status: Any | None,
    expected_device_status: Any | None,
    mock_device: CustomerDevice,
) -> None:
    """Test read_device_status."""
    mock_device.status["demo_alarm_enum"] = status
    wrapper = DPCodeInSetWrapper("demo_alarm_enum", {"alarm"})

    assert wrapper
    assert wrapper.read_device_status(mock_device) == expected_device_status
