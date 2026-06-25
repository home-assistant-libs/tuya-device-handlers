"""Tests for the csgb8eqhczvjaetl cover position quirk.

This 6Gen Roller Shutter Switch reports its position in the standard HA
convention (0=closed, 100=open). The default clkg mapping uses
``ControlBackModePercentageMappingWrapper`` which inverts the position unless
``control_back_mode`` is ``"back"``. The quirk pre-inverts the value at the
``TypeInformation`` level so the wrapper's own inversion cancels out and the
position is reported and set correctly.

See https://github.com/home-assistant/core/issues/159800.
"""

from unittest.mock import patch

import pytest

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.devices.clkg.clkg_csgb8eqhczvjaetl import (
    _InvertedIntegerTypeInformationEx,
)
from tuya_device_handlers.registry import QuirksRegistry
from tuya_device_handlers.type_information import (
    IntegerTypeInformation,
    PrepareSetValueError,
)


def test_quirk_overrides_type_information(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The quirk swaps in the inverting TypeInformation for percent_control."""
    device = create_device("clkg_csgb8eqhczvjaetl.json")
    assert "csgb8eqhczvjaetl" in filled_quirks_registry._quirks

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        type_information = IntegerTypeInformation.find_dpcode(
            device, "percent_control"
        )
    assert type_information is not None
    assert not isinstance(type_information, _InvertedIntegerTypeInformationEx)

    type_information = IntegerTypeInformation.find_dpcode(
        device, "percent_control"
    )
    assert isinstance(type_information, _InvertedIntegerTypeInformationEx)


def test_quirk_cancels_wrapper_inversion_when_forward(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """In ``forward`` mode the wrapper inverts; the quirk cancels it out."""
    device = create_device("clkg_csgb8eqhczvjaetl.json")
    device.status["control_back_mode"] = "forward"
    device.status["percent_control"] = 90

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    # Without the quirk the wrapper inverts 90 -> 10.
    read_wrapper = definitions["control"].current_position_wrapper
    write_wrapper = definitions["control"].set_position_wrapper
    assert read_wrapper is not None
    assert write_wrapper is not None
    assert read_wrapper.read_device_status(device) == 10
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 30}
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    # With the quirk the pre-inversion cancels the wrapper's inversion.
    definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    write_wrapper = definitions["control"].set_position_wrapper
    assert read_wrapper is not None
    assert write_wrapper is not None
    assert read_wrapper.read_device_status(device) == 90
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 70}
    ]


def test_quirk_inverts_when_back(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """In ``back`` mode the wrapper passes through; the quirk inverts."""
    device = create_device("clkg_csgb8eqhczvjaetl.json")
    assert device.status["control_back_mode"] == "back"
    device.status["percent_control"] = 90

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    assert read_wrapper is not None
    assert read_wrapper.read_device_status(device) == 90

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_cover_default_definitions(device)
    read_wrapper = definitions["control"].current_position_wrapper
    write_wrapper = definitions["control"].set_position_wrapper
    assert read_wrapper is not None
    assert write_wrapper is not None
    assert read_wrapper.read_device_status(device) == 10
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": 30}
    ]


def test_quirk_read_handles_missing_value(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Read returns None (not inverted) when the device reports no value."""
    device = create_device("clkg_csgb8eqhczvjaetl.json")
    filled_quirks_registry.initialise_device_quirk(device)
    del device.status["percent_control"]

    type_information = IntegerTypeInformation.find_dpcode(
        device, "percent_control"
    )
    assert type_information is not None
    assert type_information.read_device_value(device) is None


def test_quirk_write_delegates_non_numeric(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Write delegates non-numeric values to the parent class for validation."""
    device = create_device("clkg_csgb8eqhczvjaetl.json")
    filled_quirks_registry.initialise_device_quirk(device)

    type_information = IntegerTypeInformation.find_dpcode(
        device, "percent_control"
    )
    assert type_information is not None
    with pytest.raises(PrepareSetValueError):
        type_information.prepare_set_value(device, "stop")
