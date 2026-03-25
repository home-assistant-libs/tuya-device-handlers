"""Test DeviceWrapper feeder schedule functionality"""

import pytest
from syrupy.assertion import SnapshotAssertion

from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    FeederSchedule,
    get_feeder_schedule_wrapper,
)

from .. import create_device

_SAMPLE_MEAL_PLAN = [
    FeederSchedule(
        days=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
        time="09:00",
        portion=1,
        enabled=True,
    ),
    FeederSchedule(
        days=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
        time="09:30",
        portion=1,
        enabled=True,
    ),
    FeederSchedule(
        days=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
        time="12:00",
        portion=1,
        enabled=True,
    ),
    FeederSchedule(
        days=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
        time="15:00",
        portion=2,
        enabled=True,
    ),
    FeederSchedule(
        days=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
        time="21:00",
        portion=2,
        enabled=True,
    ),
]


@pytest.mark.parametrize(
    ("fixture_filename", "data"),
    [
        (
            "cwwsq_wfkzyy0evslzsmoi.json",
            "fwQAAgB/BgABAH8JAAIBfwwAAQB/DwACAX8VAAIBfxcAAQAIEgABAQ==",
        ),
        (
            "cwwsq_wfkzyy0evslzsmoi.json",
            "fwkAAQF/CR4BAX8MAAEBfw8AAgF/FQACAQ==",
        ),
        (
            "cwwsq_wfkzyy0evslzsmoi.json",
            "",
        ),
        (
            "cwwsq_wfkzyy0evslzsmoi.json",
            None,
        ),
    ],
)
def test_read_device_status(
    fixture_filename: str, data: str | None, snapshot: SnapshotAssertion
) -> None:
    """Test read_device_status decodes meal plan correctly."""
    device = create_device(fixture_filename)
    device.status["meal_plan"] = data

    wrapper = get_feeder_schedule_wrapper(device)
    assert wrapper is not None
    assert wrapper.read_device_status(device) == snapshot


def test_no_wrapper() -> None:
    """Test wrapper returns None for unsupported devices."""
    device = create_device("cl_zah67ekd.json")

    wrapper = get_feeder_schedule_wrapper(device)
    assert wrapper is None


@pytest.mark.parametrize(
    ("fixture_filename", "dpcode", "expected_value"),
    [
        (
            "cwwsq_wfkzyy0evslzsmoi.json",
            "meal_plan",
            "fwkAAQF/CR4BAX8MAAEBfw8AAgF/FQACAQ==",
        ),
    ],
)
def test_get_update_commands(
    fixture_filename: str, dpcode: str, expected_value: str
) -> None:
    """Test get_update_commands encodes data correctly."""
    device = create_device(fixture_filename)

    wrapper = get_feeder_schedule_wrapper(device)
    assert wrapper is not None

    commands = wrapper.get_update_commands(device, _SAMPLE_MEAL_PLAN)
    assert commands == [{"code": dpcode, "value": expected_value}]
