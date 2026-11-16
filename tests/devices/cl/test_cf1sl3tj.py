"""Tests for the cf1sl3tj cover position quirk.

This device reports percent_state in HA convention (0=closed, 100=open).
Without the quirk the default DPCodeInvertedPercentageWrapper incorrectly
inverts position values.

See https://github.com/home-assistant/core/issues/159800.
"""

from unittest.mock import patch

import pytest

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.registry import QuirksRegistry
from tuya_device_handlers.type_information import (
    IntegerTypeInformation,
    PrepareSetValueError,
)


def test_quirk_corrects_position(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, percent_state=90 reads as 90 (not inverted to 10)."""
    device = create_device("cl_cf1sl3tj.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 90

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 10


def test_quirk_corrects_position_write(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, setting position 70 sends raw value 70 (not 30)."""
    device = create_device("cl_cf1sl3tj.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].set_position_wrapper
    assert wrapper is not None
    assert wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 30}
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].set_position_wrapper
    assert wrapper is not None
    assert wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 70}
    ]


def test_quirk_read_handles_missing_value(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Read returns None (not inverted) when the device reports no value."""
    device = create_device("cl_cf1sl3tj.json")
    filled_quirks_registry.initialise_device_quirk(device)
    del device.status["percent_state"]

    type_information = IntegerTypeInformation.find_dpcode(
        device, "percent_state"
    )
    assert type_information is not None
    assert type_information.read_device_value(device) is None


def test_quirk_write_delegates_non_numeric(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Write delegates non-numeric values to the parent class for validation."""
    device = create_device("cl_cf1sl3tj.json")
    filled_quirks_registry.initialise_device_quirk(device)

    type_information = IntegerTypeInformation.find_dpcode(
        device, "percent_control"
    )
    assert type_information is not None
    with pytest.raises(PrepareSetValueError):
        type_information.prepare_set_value(device, "stop")
