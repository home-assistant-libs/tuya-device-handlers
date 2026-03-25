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
    "fixture_filename",
    [
        "cwwsq_wfkzyy0evslzsmoi.json",
    ],
)
def test_get_meal_data(
    fixture_filename: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get_meal_data decodes meal plan correctly."""
    device = create_device(fixture_filename)

    wrapper = get_feeder_schedule_wrapper(device)
    assert wrapper is not None
    assert wrapper.read_device_status(device) == snapshot


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
def test_get_meal_plan_update_commands(
    fixture_filename: str, dpcode: str, expected_value: str
) -> None:
    """Test get_meal_plan_update_commands encodes data correctly."""
    device = create_device(fixture_filename)

    wrapper = get_feeder_schedule_wrapper(device)
    assert wrapper is not None

    commands = wrapper.get_update_commands(device, _SAMPLE_MEAL_PLAN)
    assert commands == [{"code": dpcode, "value": expected_value}]
