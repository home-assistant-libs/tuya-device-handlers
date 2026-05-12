"""Test DeviceWrapper classes."""

from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from tuya_sharing import CustomerDevice

from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.sensor import (
    DeltaIntegerWrapper,
    ElectricityCurrentJsonWrapper,
    ElectricityCurrentRawWrapper,
    ElectricityPowerJsonWrapper,
    ElectricityPowerRawWrapper,
    ElectricityVoltageJsonWrapper,
    ElectricityVoltageRawWrapper,
    WindDirectionEnumWrapper,
)

from . import send_wrapper_update


def _snapshot_sensor(
    wrapper: DeviceWrapper[Any],
    mock_device: CustomerDevice,
    snapshot: SnapshotAssertion,
) -> None:
    """Snapshot device wrapper."""
    expected = {
        "native_unit": wrapper.native_unit,
        "state": wrapper.read_device_status(mock_device),
        "suggested_unit": wrapper.suggested_unit,
    }
    for key in ("options",):
        if hasattr(wrapper, key):
            expected[key] = getattr(wrapper, key)
    assert expected == snapshot


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "status_range", "status"),
    [
        (
            WindDirectionEnumWrapper,
            "demo_enum",
            (
                '{"range": ["north", "north_north_east", "north_east",'
                '"east_north_east","east","east_south_east","south_east",'
                '"south_south_east","south", "south_south_west", "south_west", '
                '"west_south_west", "west", "west_north_west", "north_west", '
                '"north_north_west"]}'
            ),
            "north_north_east",
        ),
        (
            DeltaIntegerWrapper,
            "demo_integer_sum",
            '{"unit": "%","min": 0,"max": 1000,"scale": 1,"step": 1}',
            123,
        ),
        (
            ElectricityCurrentJsonWrapper,
            "demo_json",
            "{}",
            '{"electricCurrent": 599.552, "power": 6.912, "voltage": 52.7}',
        ),
        (
            ElectricityPowerJsonWrapper,
            "demo_json",
            "{}",
            '{"electricCurrent": 599.552, "power": 6.912, "voltage": 52.7}',
        ),
        (
            ElectricityVoltageJsonWrapper,
            "demo_json",
            "{}",
            '{"electricCurrent": 599.552, "power": 6.912, "voltage": 52.7}',
        ),
        (
            ElectricityCurrentRawWrapper,
            "demo_raw",
            "{}",
            "Ag8JJQAASAAACAAAAAAACGME",
        ),
        (
            ElectricityPowerRawWrapper,
            "demo_raw",
            "{}",
            "Ag8JJQAASAAACAAAAAAACGME",
        ),
        (
            ElectricityVoltageRawWrapper,
            "demo_raw",
            "{}",
            "Ag8JJQAASAAACAAAAAAACGME",
        ),
    ],
)
def test_sensor_wrapper(
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    dpcode: str,
    status_range: str,
    status: Any,
    mock_device: CustomerDevice,
    snapshot: SnapshotAssertion,
) -> None:
    """Test sensor wrappers."""
    mock_device.status[dpcode] = status
    mock_device.status_range[dpcode].values = status_range
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    _snapshot_sensor(wrapper, mock_device, snapshot)


@pytest.mark.parametrize(
    ("wrapper_type", "dpcode", "status_range", "status"),
    [
        (
            WindDirectionEnumWrapper,
            "demo_enum",
            (
                '{"range": ["north", "north_north_east", "north_east",'
                '"east_north_east","east","east_south_east","south_east",'
                '"south_south_east","south", "south_south_west", "south_west", '
                '"west_south_west", "west", "west_north_west", "north_west", '
                '"north_north_west"]}'
            ),
            "north_northh_east",
        ),
        (
            ElectricityCurrentJsonWrapper,
            "demo_json",
            "{}",
            "{}",
        ),
        (
            ElectricityPowerJsonWrapper,
            "demo_json",
            "{}",
            "{}",
        ),
        (
            ElectricityVoltageJsonWrapper,
            "demo_json",
            "{}",
            "{}",
        ),
        (
            ElectricityCurrentRawWrapper,
            "demo_raw",
            "{}",
            "",
        ),
        (
            ElectricityPowerRawWrapper,
            "demo_raw",
            "{}",
            "",
        ),
        (
            ElectricityVoltageRawWrapper,
            "demo_raw",
            "{}",
            "",
        ),
    ],
)
def test_sensor_invalid_value(
    wrapper_type: type[DPCodeTypeInformationWrapper[Any, Any, Any]],
    dpcode: str,
    status_range: str,
    status: str,
    mock_device: CustomerDevice,
) -> None:
    """Test sensor wrappers with invalid or None value."""
    mock_device.status[dpcode] = status
    mock_device.status_range[dpcode].values = status_range
    wrapper = wrapper_type.find_dpcode(mock_device, dpcode)

    assert wrapper
    assert wrapper.read_device_status(mock_device) is None

    # All wrappers return None if status is None
    mock_device.status[dpcode] = None
    assert wrapper.read_device_status(mock_device) is None


def test_delta_sensor(
    mock_device: CustomerDevice,
) -> None:
    """Test DeltaIntegerWrapper wrapper."""
    dpcode = "demo_integer_sum"
    timestamp = 123456789
    wrapper = DeltaIntegerWrapper.find_dpcode(mock_device, dpcode)

    assert wrapper
    wrapper.initialize(mock_device)
    assert wrapper.read_device_status(mock_device) == 0

    # Send delta update
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer_sum": 200},
        {"demo_integer_sum": timestamp},
    )
    assert wrapper.read_device_status(mock_device) == 20

    # Send delta update
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer_sum": 200},
        {"demo_integer_sum": timestamp},
    )
    assert wrapper.read_device_status(mock_device) == 20

    # Send delta update (multiple dpcode)
    timestamp += 100
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer_sum": 100, "demo_integer": 100},
        {"demo_integer_sum": timestamp, "demo_integer": timestamp},
    )
    assert wrapper.read_device_status(mock_device) == 30

    # Send delta update (timestamp not incremented)
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer_sum": 100, "demo_integer": 100},
        {"demo_integer_sum": timestamp, "demo_integer": timestamp},
    )
    assert wrapper.read_device_status(mock_device) == 30  # unchanged

    # Send delta update (unrelated dpcode)
    timestamp += 100
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer": 100},
        {"demo_integer": timestamp},
    )
    assert wrapper.read_device_status(mock_device) == 30  # unchanged

    # Send delta update
    timestamp += 100
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer_sum": 50, "demo_integer": 100},
        {"demo_integer_sum": timestamp, "demo_integer": timestamp},
    )
    assert wrapper.read_device_status(mock_device) == 35

    # Send delta update (None value)
    timestamp += 100
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer_sum": None},
        {"demo_integer_sum": timestamp},
    )
    assert wrapper.read_device_status(mock_device) == 35  # unchanged

    # Send delta update (no timestamp - skipped)
    send_wrapper_update(
        mock_device,
        wrapper,
        {"demo_integer_sum": 200},
        None,
    )
    assert wrapper.read_device_status(mock_device) == 35  # unchanged
