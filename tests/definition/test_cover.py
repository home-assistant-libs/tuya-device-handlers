"""Tests for cover definition."""

from typing import Any

import pytest
from tuya_sharing import CustomerDevice

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder.device_quirk import DeviceQuirk
from tuya_device_handlers.definition.cover import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeIntegerWrapper
from tuya_device_handlers.device_wrapper.cover import (
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
