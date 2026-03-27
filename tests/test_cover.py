"""Test utils"""

import dataclasses
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.builder import TuyaCoverDefinition
from tuya_device_handlers.device_wrapper.common import (
    DPCodeIntegerWrapper,
    DPCodeWrapper,
)
from tuya_device_handlers.registry import QuirksRegistry

from . import create_device
from .const import DEVICE_FIXTURES


def _get_entity_details(
    definition: TuyaCoverDefinition, device: CustomerDevice
) -> dict[str, Any]:
    """Generate snapshot details."""
    entity_details: dict[str, Any] = {
        "get_state_dp_code": None,
        "set_state_dp_code": None,
        "get_position_dp_code": None,
        "set_position_dp_code": None,
        "state": None,
    }

    get_state_dp_type = definition.get_state_dp_type(device)
    set_state_dp_type = definition.set_state_dp_type(device)
    get_position_dp_type = definition.get_position_dp_type(device)
    set_position_dp_type = definition.set_position_dp_type(device)

    if get_state_dp_type and isinstance(get_state_dp_type, DPCodeWrapper):
        entity_details["get_state_dp_code"] = get_state_dp_type.dpcode
        if (status := device.status.get(get_state_dp_type.dpcode)) is not None:
            entity_details["state"] = status

    if set_state_dp_type and isinstance(set_state_dp_type, DPCodeWrapper):
        entity_details["set_state_dp_code"] = set_state_dp_type.dpcode

    if get_position_dp_type and isinstance(
        get_position_dp_type, DPCodeIntegerWrapper
    ):
        entity_details["get_position_dp_code"] = get_position_dp_type.dpcode
        if (
            status := device.status.get(get_position_dp_type.dpcode)
        ) is not None:
            entity_details["position"] = (
                get_position_dp_type.type_information.scale_value(status)
            )

    if set_position_dp_type and isinstance(set_position_dp_type, DPCodeWrapper):
        entity_details["set_position_dp_code"] = set_position_dp_type.dpcode

    return entity_details


@pytest.mark.parametrize("fixture_filename", DEVICE_FIXTURES)
def test_entities(
    fixture_filename: str,
    filled_quirks_registry: QuirksRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test entities."""
    device = create_device(fixture_filename)

    quirk = filled_quirks_registry.get_quirk_for_device(device)
    assert quirk is not None
    for definition in quirk.cover_quirks or ():
        assert dataclasses.asdict(definition) == snapshot(
            name=f"{definition.key}-definition",
            exclude=props(
                "get_state_dp_type",
                "set_state_dp_type",
                "get_position_dp_type",
                "set_position_dp_type",
            ),
        )
        assert _get_entity_details(definition, device) == snapshot(
            name=f"{definition.key}-state"
        )
