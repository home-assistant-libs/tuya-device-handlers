"""Test extended TypeInformation classes."""

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.type_information import PrepareSetValueError
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)


def _find(device: CustomerDevice) -> InvertedIntegerTypeInformationEx:
    """Return the inverted type information for ``demo_integer``."""
    # demo_integer: min=0, max=1000, scale=1, step=1 => scaled range 0-100.
    type_information = InvertedIntegerTypeInformationEx.find_dpcode(
        device, "demo_integer"
    )
    assert type_information is not None
    return type_information


def test_read_inverts_within_range(mock_device: CustomerDevice) -> None:
    """Read returns ``scale_value(max) - value``."""
    mock_device.status["demo_integer"] = 123
    type_information = _find(mock_device)
    # scale_value(1000) - scale_value(123) = 100 - 12.3 = 87.7
    value = type_information.read_device_value(mock_device)
    assert value == pytest.approx(87.7)


def test_read_handles_missing_value(mock_device: CustomerDevice) -> None:
    """Read returns ``None`` (not inverted) when no value is reported."""
    del mock_device.status["demo_integer"]
    type_information = _find(mock_device)
    assert type_information.read_device_value(mock_device) is None


def test_write_inverts_within_range(mock_device: CustomerDevice) -> None:
    """Write sends the inverted raw value to the device."""
    type_information = _find(mock_device)
    # scale_value(1000) - 70 = 30 => scale_value_back(30) = 300
    assert type_information.prepare_set_value(mock_device, 70) == 300


def test_write_delegates_non_numeric(mock_device: CustomerDevice) -> None:
    """Write delegates non-numeric values to the parent for validation."""
    type_information = _find(mock_device)
    with pytest.raises(PrepareSetValueError):
        type_information.prepare_set_value(mock_device, "stop")


def test_inversion_round_trips(mock_device: CustomerDevice) -> None:
    """A value read back after writing returns to its original."""
    type_information = _find(mock_device)
    raw = type_information.prepare_set_value(mock_device, 70)
    mock_device.status["demo_integer"] = raw
    assert type_information.read_device_value(mock_device) == pytest.approx(70)
