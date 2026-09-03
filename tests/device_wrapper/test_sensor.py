"""Test DeviceWrapper classes."""

from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from tuya_sharing import CustomerDevice

from tests import create_device
from tuya_device_handlers.device_wrapper import DeviceWrapper
from tuya_device_handlers.device_wrapper.common import (
    DPCodeTypeInformationWrapper,
)
from tuya_device_handlers.device_wrapper.sensor import (
    DeltaIntegerWrapper,
    ElectricityApparentPowerHexStringWrapper,
    ElectricityApparentPowerJsonWrapper,
    ElectricityApparentPowerRawWrapper,
    ElectricityCurrentHexStringWrapper,
    ElectricityCurrentJsonWrapper,
    ElectricityCurrentRawWrapper,
    ElectricityPowerFactorHexStringWrapper,
    ElectricityPowerFactorJsonWrapper,
    ElectricityPowerFactorRawWrapper,
    ElectricityPowerHexStringWrapper,
    ElectricityPowerJsonWrapper,
    ElectricityPowerRawWrapper,
    ElectricityReactivePowerHexStringWrapper,
    ElectricityReactivePowerJsonWrapper,
    ElectricityReactivePowerRawWrapper,
    ElectricityVoltageHexStringWrapper,
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
            ElectricityReactivePowerJsonWrapper,
            "demo_json",
            "{}",
            '{"reactivePower": 0.5, "apparentPower": 0.9, "powerFactor": 0.9}',
        ),
        (
            ElectricityApparentPowerJsonWrapper,
            "demo_json",
            "{}",
            '{"reactivePower": 0.5, "apparentPower": 0.9, "powerFactor": 0.9}',
        ),
        (
            ElectricityPowerFactorJsonWrapper,
            "demo_json",
            "{}",
            '{"reactivePower": 0.5, "apparentPower": 0.9, "powerFactor": 0.9}',
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
        (
            ElectricityReactivePowerRawWrapper,
            "demo_raw",
            "{}",
            "Ag8JJQAASAAACAAAAAAACGME",
        ),
        (
            ElectricityApparentPowerRawWrapper,
            "demo_raw",
            "{}",
            "Ag8JJQAASAAACAAAAAAACGME",
        ),
        (
            ElectricityPowerFactorRawWrapper,
            "demo_raw",
            "{}",
            "Ag8JJQAASAAACAAAAAAACGME",
        ),
        (
            ElectricityCurrentHexStringWrapper,
            "demo_string",
            "{}",
            "020F09010027100008FC0001F400092E6200",
        ),
        (
            ElectricityPowerHexStringWrapper,
            "demo_string",
            "{}",
            "020F09010027100008FC0001F400092E6200",
        ),
        (
            ElectricityVoltageHexStringWrapper,
            "demo_string",
            "{}",
            "020F09010027100008FC0001F400092E6200",
        ),
        (
            ElectricityReactivePowerHexStringWrapper,
            "demo_string",
            "{}",
            "020F09010027100008FC0001F400092E6200",
        ),
        (
            ElectricityApparentPowerHexStringWrapper,
            "demo_string",
            "{}",
            "020F09010027100008FC0001F400092E6200",
        ),
        (
            ElectricityPowerFactorHexStringWrapper,
            "demo_string",
            "{}",
            "020F09010027100008FC0001F400092E6200",
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
            ElectricityReactivePowerJsonWrapper,
            "demo_json",
            "{}",
            "{}",
        ),
        (
            ElectricityApparentPowerJsonWrapper,
            "demo_json",
            "{}",
            "{}",
        ),
        (
            ElectricityPowerFactorJsonWrapper,
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
        (
            ElectricityReactivePowerRawWrapper,
            "demo_raw",
            "{}",
            "",
        ),
        (
            ElectricityApparentPowerRawWrapper,
            "demo_raw",
            "{}",
            "",
        ),
        (
            ElectricityPowerFactorRawWrapper,
            "demo_raw",
            "{}",
            "",
        ),
        (
            ElectricityCurrentHexStringWrapper,
            "demo_string",
            "{}",
            "not-hex",
        ),
        (
            ElectricityPowerHexStringWrapper,
            "demo_string",
            "{}",
            "not-hex",
        ),
        (
            ElectricityVoltageHexStringWrapper,
            "demo_string",
            "{}",
            "not-hex",
        ),
        (
            ElectricityReactivePowerHexStringWrapper,
            "demo_string",
            "{}",
            "not-hex",
        ),
        (
            ElectricityApparentPowerHexStringWrapper,
            "demo_string",
            "{}",
            "not-hex",
        ),
        (
            ElectricityPowerFactorHexStringWrapper,
            "demo_string",
            "{}",
            "not-hex",
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


def test_electricity_raw_wrappers_real_device(
    snapshot: SnapshotAssertion,
) -> None:
    """Test the electricity raw wrappers against a real v02 phase frame.

    `dlq_cnpkf4xdmd9v49iq` is the only device fixture carrying an 18-byte
    v02 frame, so it is the only real-world check that the six-parameter
    layout is decoded the way the device reports it.
    """
    device = create_device("dlq_cnpkf4xdmd9v49iq.json")
    dpcode = "phase_a"

    states = {}
    for wrapper_type in (
        ElectricityCurrentRawWrapper,
        ElectricityPowerRawWrapper,
        ElectricityVoltageRawWrapper,
        ElectricityReactivePowerRawWrapper,
        ElectricityApparentPowerRawWrapper,
        ElectricityPowerFactorRawWrapper,
    ):
        wrapper = wrapper_type.find_dpcode(device, dpcode)
        assert wrapper
        states[wrapper_type.__name__] = wrapper.read_device_status(device)

    assert states == snapshot


def test_electricity_json_wrappers_real_device(
    snapshot: SnapshotAssertion,
) -> None:
    """Test the electricity JSON wrappers against a real zndb meter.

    `zndb_iow5ux77dxy3yrpj` reports the phase datapoints as JSON, so it is
    the real-world check that the six JSON keys (including reactive/apparent
    power and power factor) are read the way the meter reports them.
    """
    device = create_device("zndb_iow5ux77dxy3yrpj.json")
    dpcode = "phase_a"

    states = {}
    for wrapper_type in (
        ElectricityCurrentJsonWrapper,
        ElectricityPowerJsonWrapper,
        ElectricityVoltageJsonWrapper,
        ElectricityReactivePowerJsonWrapper,
        ElectricityApparentPowerJsonWrapper,
        ElectricityPowerFactorJsonWrapper,
    ):
        wrapper = wrapper_type.find_dpcode(device, dpcode)
        assert wrapper
        states[wrapper_type.__name__] = wrapper.read_device_status(device)

    assert states == snapshot


def test_electricity_hex_string_wrappers_real_device(
    snapshot: SnapshotAssertion,
) -> None:
    """Test the electricity hex-string wrappers against a real zndb meter.

    `zndb_uqzhc4bx5zqwpg2m` is a multi-metering meter that reports its phase
    datapoints as hex-encoded frame strings (`phase_s*`), so it is the
    real-world check that the hex-string wrappers decode the frame the way
    the meter reports it.
    """
    device = create_device("zndb_uqzhc4bx5zqwpg2m.json")
    dpcode = "phase_s1"

    states = {}
    for wrapper_type in (
        ElectricityCurrentHexStringWrapper,
        ElectricityPowerHexStringWrapper,
        ElectricityVoltageHexStringWrapper,
        ElectricityReactivePowerHexStringWrapper,
        ElectricityApparentPowerHexStringWrapper,
        ElectricityPowerFactorHexStringWrapper,
    ):
        wrapper = wrapper_type.find_dpcode(device, dpcode)
        assert wrapper
        states[wrapper_type.__name__] = wrapper.read_device_status(device)

    assert states == snapshot
