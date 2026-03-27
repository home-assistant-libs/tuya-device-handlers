"""Test utils"""

import dataclasses
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.builder import TuyaSelectDefinition
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry

from . import create_device
from .const import DEVICE_FIXTURES


def _get_entity_details(
    definition: TuyaSelectDefinition, device: CustomerDevice
) -> dict[str, Any]:
    """Generate snapshot details."""
    entity_details: dict[str, Any] = {
        "dp_code": None,
        "options": None,
        "state": None,
    }

    if (
        enum_definition := definition.dp_type(device)
    ) is not None and isinstance(enum_definition, DPCodeEnumWrapper):
        entity_details["dp_code"] = enum_definition.dpcode
        entity_details["options"] = enum_definition.options
        if (
            status := device.status.get(definition.key)
        ) is not None and status in enum_definition.options:
            entity_details["state"] = status

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
    for definition in quirk.select_quirks or ():
        assert dataclasses.asdict(definition) == snapshot(
            name=f"{definition.key}-definition",
            exclude=props("dp_type"),
        )
        assert _get_entity_details(definition, device) == snapshot(
            name=f"{definition.key}-state"
        )
