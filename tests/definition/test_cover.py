"""Tests for cover definition."""

from typing import Any
from unittest.mock import patch

import pytest
from tuya_sharing import CustomerDevice, DeviceFunction, DeviceStatusRange

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder.device_quirk import DeviceQuirk
from tuya_device_handlers.definition.cover import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeIntegerWrapper
from tuya_device_handlers.device_wrapper.cover import (
    ControlBackModePercentageMappingWrapper,
    CoverClosedEnumWrapper,
    CoverInstructionEnumWrapper,
)
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
)
from tuya_device_handlers.type_information import IntegerTypeInformation


def test_get_default_definition() -> None:
    """Test get_default_definition."""
    device = create_device("cl_zah67ekd.json")
    assert (
        definition := get_default_definition(
            device,
            current_position_dpcode=("percent_state", "percent_control"),
            current_state_dpcode=("situation_set", "control"),
            instruction_dpcode="control",
            set_position_dpcode="percent_control",
            current_state_wrapper=CoverClosedEnumWrapper,
            instruction_wrapper=CoverInstructionEnumWrapper,
            position_wrapper=DPCodeInvertedPercentageWrapper,
        )
    )
    assert isinstance(
        definition.current_position_wrapper, DPCodeInvertedPercentageWrapper
    )
    assert isinstance(definition.current_state_wrapper, CoverClosedEnumWrapper)
    assert isinstance(
        definition.instruction_wrapper, CoverInstructionEnumWrapper
    )
    assert isinstance(
        definition.set_position_wrapper, DPCodeInvertedPercentageWrapper
    )
    assert not definition.tilt_position_wrapper


def test_get_default_definition_fails() -> None:
    """Test get_default_definition."""
    device = create_device("cl_zah67ekd.json")
    assert not get_default_definition(
        device,
        current_position_dpcode="bad",
        current_state_dpcode="bad",
        instruction_dpcode="bad",
        set_position_dpcode="bad",
        current_state_wrapper=CoverClosedEnumWrapper,
        instruction_wrapper=CoverInstructionEnumWrapper,
        position_wrapper=DPCodeInvertedPercentageWrapper,
    )


class _InvertedPercentageIntegerTypeInformation(IntegerTypeInformation):
    """Inverts a 0-100 percentage on read and write."""

    def read_device_value(self, device: CustomerDevice) -> float | None:
        value = super().read_device_value(device)
        if value is None:
            return None
        return self.max - value

    def prepare_set_value(self, device: CustomerDevice, value: Any) -> int:
        if not isinstance(value, (int, float)):
            return super().prepare_set_value(device, value)
        return super().prepare_set_value(device, self.max - value)


@pytest.mark.parametrize(
    (
        "type_information_cls_override",
        "expected_position",
        "expected_raw_write",
    ),
    [
        # Default: raw value pass-through (read 52, write 70 → 70).
        (IntegerTypeInformation, 52, 70),
        # Inverted: percent_state 52 reads as 48; HA value 70 writes as 30.
        (_InvertedPercentageIntegerTypeInformation, 48, 30),
    ],
)
def test_cover_position_quirk_type_information_override(
    type_information_cls_override: type[IntegerTypeInformation],
    expected_position: int,
    expected_raw_write: int,
) -> None:
    """A quirk-supplied TypeInformation flows through to the cover wrapper."""
    device = create_device("cl_zah67ekd.json")
    (
        DeviceQuirk()
        .applies_to(product_id=device.product_id)
        .override_dpid_type_information_cls(
            dpid=3,
            dpcode="percent_state",
            type_information_cls=type_information_cls_override,
        )
        .register(TUYA_QUIRKS_REGISTRY)
    )

    definition = get_default_definition(
        device,
        current_position_dpcode=("percent_state", "percent_control"),
        instruction_dpcode="control",
        set_position_dpcode="percent_control",
        position_wrapper=DPCodeIntegerWrapper,
    )
    assert definition is not None
    position_wrapper = definition.current_position_wrapper
    assert isinstance(position_wrapper, DPCodeIntegerWrapper)
    assert position_wrapper.dpcode == "percent_state"
    assert isinstance(
        position_wrapper.type_information, type_information_cls_override
    )
    assert position_wrapper.read_device_status(device) == expected_position
    assert position_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_state", "value": expected_raw_write}
    ]


@pytest.mark.parametrize(
    "position_wrapper",
    [
        # What Home Assistant Core passes for clkg today
        ControlBackModePercentageMappingWrapper,
        # What it will use once the category override is removed
        DPCodeInvertedPercentageWrapper,
    ],
)
@pytest.mark.parametrize(
    ("control_back_mode", "expected_position", "expected_raw_write"),
    [("back", 25, 70), ("forward", 75, 30), (None, 75, 30)],
)
def test_clkg_position_without_quirk(
    position_wrapper: type[DPCodeInvertedPercentageWrapper],
    control_back_mode: str | None,
    expected_position: int,
    expected_raw_write: int,
) -> None:
    """A clkg position follows control_back_mode, whichever wrapper is used."""
    device = create_device("clkg_csgb8eqhczvjaetl.json")
    device.status["percent_control"] = 25
    device.status["control_back_mode"] = control_back_mode
    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definition = get_default_definition(
            device,
            current_position_dpcode="percent_control",
            instruction_dpcode="control",
            position_wrapper=position_wrapper,
            set_position_dpcode="percent_control",
        )
    assert definition is not None
    assert definition.current_position_wrapper is not None
    assert definition.set_position_wrapper is not None

    assert (
        definition.current_position_wrapper.read_device_status(device)
        == expected_position
    )
    assert definition.set_position_wrapper.get_update_commands(device, 70) == [
        {"code": "percent_control", "value": expected_raw_write}
    ]


@pytest.mark.parametrize(
    "position_wrapper",
    [
        ControlBackModePercentageMappingWrapper,
        DPCodeInvertedPercentageWrapper,
    ],
)
@pytest.mark.parametrize(
    ("control_back_mode", "expected_position", "expected_raw_write"),
    [("back", 19, 66), ("forward", 81, 34), (None, 81, 34)],
)
@pytest.mark.parametrize(
    ("dpcode", "wrapper_attributes"),
    [
        (
            "percent_control",
            ("current_position_wrapper", "set_position_wrapper"),
        ),
        (
            "angle_horizontal",
            ("tilt_position_wrapper", "tilt_position_wrapper"),
        ),
    ],
)
def test_clkg_position_and_tilt_nonzero_range(
    position_wrapper: type[DPCodeInvertedPercentageWrapper],
    control_back_mode: str | None,
    expected_position: int,
    expected_raw_write: int,
    dpcode: str,
    wrapper_attributes: tuple[str, str],
) -> None:
    """Position and tilt follow control_back_mode, for any range."""
    device = create_device("clkg_csgb8eqhczvjaetl.json")
    values = '{"unit":"%","min":10,"max":90,"scale":0,"step":1}'
    device.function[dpcode] = DeviceFunction(
        code=dpcode, type="Integer", values=values
    )
    device.status_range[dpcode] = DeviceStatusRange(
        code=dpcode, type="Integer", values=values
    )
    device.status[dpcode] = 25
    device.status["control_back_mode"] = control_back_mode
    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definition = get_default_definition(
            device,
            current_position_dpcode="percent_control",
            instruction_dpcode="control",
            position_wrapper=position_wrapper,
            set_position_dpcode="percent_control",
        )
    assert definition is not None
    read_wrapper = getattr(definition, wrapper_attributes[0])
    write_wrapper = getattr(definition, wrapper_attributes[1])

    assert read_wrapper.read_device_status(device) == expected_position
    assert write_wrapper.get_update_commands(device, 70) == [
        {"code": dpcode, "value": expected_raw_write}
    ]
