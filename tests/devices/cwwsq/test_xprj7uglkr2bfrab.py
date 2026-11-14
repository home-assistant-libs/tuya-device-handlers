"""Test the WiFi Feeder quirk (reversed day bitmask)."""

from unittest.mock import patch

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    FeederSchedule,
)
from tuya_device_handlers.registry import QuirksRegistry

_FIXTURE = "cwwsq_xprj7uglkr2bfrab.json"

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]

# Sunday is bit 0, Saturday bit 1, ..., Monday bit 6 (checked on a real device
# by moving single entries in the Tuya app).
_MEAL_PLAN = [
    FeederSchedule(days=["sunday"], time="12:00", portion=1, enabled=True),
    FeederSchedule(days=["saturday"], time="12:01", portion=1, enabled=True),
    FeederSchedule(days=_WEEKDAYS, time="12:00", portion=1, enabled=True),
    FeederSchedule(days=["thursday"], time="09:35", portion=2, enabled=False),
    FeederSchedule(days=["monday"], time="17:00", portion=1, enabled=True),
]
# Entries: 01 0c 00 01 01 | 02 0c 01 01 01 | 7c 0c 00 01 01 | ...
# (days mask, hour, minute, portion, enabled)
_RAW = "AQwAAQECDAEBAXwMAAEBCAkjAgBAEQABAQ=="


def test_read_device_status(filled_quirks_registry: QuirksRegistry) -> None:
    """Days are decoded with Sunday as bit 0."""
    device = create_device(_FIXTURE)
    device.status["meal_plan"] = _RAW

    assert (quirk := filled_quirks_registry.get_quirk_for_device(device))
    assert (wrapper := quirk.get_feeder_schedules_wrapper(device))
    assert wrapper.read_device_status(device) == _MEAL_PLAN


def test_get_update_commands(filled_quirks_registry: QuirksRegistry) -> None:
    """Days are encoded with Sunday as bit 0."""
    device = create_device(_FIXTURE)

    assert (quirk := filled_quirks_registry.get_quirk_for_device(device))
    assert (wrapper := quirk.get_feeder_schedules_wrapper(device))
    assert wrapper.get_update_commands(device, _MEAL_PLAN) == [
        {"code": "meal_plan", "value": _RAW}
    ]


def test_not_supported_without_quirk() -> None:
    """Without the quirk, the device has no feeder schedule wrapper."""
    device = create_device(_FIXTURE)

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        assert TUYA_QUIRKS_REGISTRY.get_quirk_for_device(device) is None
