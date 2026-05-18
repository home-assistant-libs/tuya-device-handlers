"""Test device-level quirk initialisation."""

import pytest
from syrupy.assertion import SnapshotAssertion

from tests import create_device
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    FeederSchedule,
)
from tuya_device_handlers.registry import QuirksRegistry

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
    fixture_filename: str,
    data: str | None,
    filled_quirks_registry: QuirksRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test read_device_status decodes meal plan correctly."""
    device = create_device(fixture_filename)
    device.status["meal_plan"] = data

    assert (quirk := filled_quirks_registry.get_quirk_for_device(device))
    assert (wrapper := quirk.get_feeder_schedules_wrapper(device))

    assert wrapper.read_device_status(device) == snapshot


def test_get_update_commands(filled_quirks_registry: QuirksRegistry) -> None:
    """Test get_update_commands encodes data correctly."""
    device = create_device("cwwsq_wfkzyy0evslzsmoi.json")

    assert (quirk := filled_quirks_registry.get_quirk_for_device(device))
    assert (wrapper := quirk.get_feeder_schedules_wrapper(device))

    assert wrapper.get_update_commands(device, _SAMPLE_MEAL_PLAN) == [
        {"code": "meal_plan", "value": "fwkAAQF/CR4BAX8MAAEBfw8AAgF/FQACAQ=="}
    ]
