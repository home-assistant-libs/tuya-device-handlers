"""Test fixtures."""

import json
import pathlib
from typing import Any

import pytest

_FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures" / "devices"
_DEVICE_MOCKS = sorted(
    str(path.relative_to(_FIXTURES_DIR).with_suffix(""))
    for path in _FIXTURES_DIR.glob("*.json")
)

# We want to ensure that the fixture files do not contain
# `home_assistant`, `id`, or `terminal_id` keys.
# These are provided by the Tuya diagnostics and should be removed
# from the fixture.
_EXCLUDE_KEYS = ("home_assistant", "id", "terminal_id")

_REDACTED_DPCODES = {
    "alarm_message",
    "alarm_msg",
    "doorbell_pic",
    "movement_detect_pic",
}


@pytest.mark.parametrize("device_code", _DEVICE_MOCKS)
def test_fixtures_valid(device_code: str) -> None:
    """Ensure Tuya fixture files are valid."""
    with open(f"tests/fixtures/devices/{device_code}.json") as fixture_file:
        details: dict[str, Any] = json.load(fixture_file)
    for key in _EXCLUDE_KEYS:
        assert key not in details, (
            f"Please remove data[`'{key}']` from {device_code}.json"
        )
    if "status" in details:
        statuses = details["status"]
        for key in statuses:
            if key in _REDACTED_DPCODES:
                assert statuses[key] == "**REDACTED**", (
                    f"Please mark `data['status']['{key}']` as `**REDACTED**`"
                    f" in {device_code}.json"
                )
