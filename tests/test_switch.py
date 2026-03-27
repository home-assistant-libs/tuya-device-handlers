"""Test utils"""

import dataclasses
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.builder import TuyaSwitchDefinition
from tuya_device_handlers.registry import QuirksRegistry

from . import create_device
from .const import DEVICE_FIXTURES


def _get_entity_details(
    definition: TuyaSwitchDefinition, device: CustomerDevice
) -> dict[str, Any]:
    """Generate snapshot details."""
    entity_details = {}
    value = device.status.get(definition.key)

    entity_details["state"] = value
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
    for definition in quirk.switch_quirks or ():
        assert dataclasses.asdict(definition) == snapshot(
            name=f"{definition.key}-definition"
        )
        assert _get_entity_details(definition, device) == snapshot(
            name=f"{definition.key}-state"
        )
