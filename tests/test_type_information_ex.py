"""Tests for type_information_ex classes."""

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)


def _make_type_info(
    *, min: int = 0, max: int = 100, scale: int = 0, step: int = 1
) -> InvertedIntegerTypeInformationEx:
    return InvertedIntegerTypeInformationEx(
        dpcode="percent_state",
        type_data="{}",
        report_type=None,
        min=min,
        max=max,
        scale=scale,
        step=step,
    )


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        (0, 100.0),
        (52, 48.0),
        (100, 0.0),
    ],
)
def test_read_device_value_inverts(
    mock_device: CustomerDevice,
    raw_value: int,
    expected: float,
) -> None:
    """read_device_value returns max - value."""
    mock_device.status["percent_state"] = raw_value
    type_info = _make_type_info()
    assert type_info.read_device_value(mock_device) == expected


def test_read_device_value_none(mock_device: CustomerDevice) -> None:
    """read_device_value returns None when dpcode is absent."""
    mock_device.status.pop("percent_state", None)
    type_info = _make_type_info()
    assert type_info.read_device_value(mock_device) is None


@pytest.mark.parametrize(
    ("ha_value", "expected_raw"),
    [
        (0, 100),
        (52, 48),
        (70, 30),
        (100, 0),
    ],
)
def test_prepare_set_value_inverts(
    mock_device: CustomerDevice,
    ha_value: int,
    expected_raw: int,
) -> None:
    """prepare_set_value sends max - value to the device."""
    type_info = _make_type_info()
    assert type_info.prepare_set_value(mock_device, ha_value) == expected_raw


def test_read_device_value_scaled(mock_device: CustomerDevice) -> None:
    """Inversion is applied after scaling (scale=1, range 0-1000)."""
    mock_device.status["percent_state"] = 520
    type_info = _make_type_info(max=1000, scale=1)
    assert type_info.read_device_value(mock_device) == pytest.approx(48.0)


def test_prepare_set_value_scaled(mock_device: CustomerDevice) -> None:
    """Inversion is applied before scale-back (scale=1, range 0-1000)."""
    type_info = _make_type_info(max=1000, scale=1)
    assert type_info.prepare_set_value(mock_device, 70.0) == 300
