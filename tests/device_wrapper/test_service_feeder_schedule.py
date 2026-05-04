"""Test DeviceWrapper feeder schedule functionality"""

import pytest
from syrupy.assertion import SnapshotAssertion
from tuya_sharing import CustomerDevice

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder.device_quirk import DeviceQuirk
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    DefaultFeederScheduleWrapper,
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

    wrapper = DefaultFeederScheduleWrapper.find_dpcode(
        device, "meal_plan", prefer_function=True
    )
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
def test_get_update_commands(
    fixture_filename: str, dpcode: str, expected_value: str
) -> None:
    """Test get_update_commands encodes data correctly."""
    device = create_device(fixture_filename)

    wrapper = DefaultFeederScheduleWrapper.find_dpcode(
        device, "meal_plan", prefer_function=True
    )
    assert wrapper is not None

    commands = wrapper.get_update_commands(device, _SAMPLE_MEAL_PLAN)
    assert commands == [{"code": dpcode, "value": expected_value}]


def test_get_feeder_schedule_wrapper_unknown() -> None:
    """Test get_feeder_schedule_wrapper returns no wrapper."""
    device = create_device("cl_zah67ekd.json")
    wrapper = get_feeder_schedule_wrapper(device)
    assert wrapper is None


def test_get_fallback_feeder_schedule_wrapper() -> None:
    """Test get_feeder_schedule_wrapper returns the fallback wrapper."""
    device = create_device("cwwsq_wfkzyy0evslzsmoi.json")
    wrapper = get_feeder_schedule_wrapper(device)
    assert isinstance(wrapper, DefaultFeederScheduleWrapper)


def test_get_quirk_feeder_schedule_wrapper(mock_device: CustomerDevice) -> None:
    """Test get_feeder_schedule_wrapper returns the quirk wrapper."""
    wrapper = get_feeder_schedule_wrapper(mock_device)
    assert wrapper is None

    (
        DeviceQuirk()
        .applies_to(product_id=mock_device.product_id)
        .map_feeder_schedules_wrapper(
            wrapper_function=lambda device: (
                DefaultFeederScheduleWrapper.find_dpcode(
                    device, "demo_raw", prefer_function=True
                )
            )
        )
        .register(TUYA_QUIRKS_REGISTRY)
    )

    wrapper = get_feeder_schedule_wrapper(mock_device)
    assert isinstance(wrapper, DefaultFeederScheduleWrapper)


def test_get_quirk_feeder_schedule_wrapper_invalid(
    mock_device: CustomerDevice,
) -> None:
    """Test get_feeder_schedule_wrapper returns the quirk wrapper."""
    wrapper = get_feeder_schedule_wrapper(mock_device)
    assert wrapper is None

    (
        DeviceQuirk()
        .applies_to(product_id=mock_device.product_id)
        .map_feeder_schedules_wrapper(
            wrapper_function=lambda device: (
                DefaultFeederScheduleWrapper.find_dpcode(
                    device, "invalid", prefer_function=True
                )
            )
        )
        .register(TUYA_QUIRKS_REGISTRY)
    )

    wrapper = get_feeder_schedule_wrapper(mock_device)
    assert wrapper is None


def test_get_quirk_feeder_schedule_wrapper_not_set(
    mock_device: CustomerDevice,
) -> None:
    """Test get_feeder_schedule_wrapper returns the quirk wrapper."""
    wrapper = get_feeder_schedule_wrapper(mock_device)
    assert wrapper is None

    (
        DeviceQuirk()
        .applies_to(product_id=mock_device.product_id)
        .register(TUYA_QUIRKS_REGISTRY)
    )

    wrapper = get_feeder_schedule_wrapper(mock_device)
    assert wrapper is None
