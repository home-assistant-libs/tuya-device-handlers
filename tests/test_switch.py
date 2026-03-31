"""Test utils"""

import dataclasses
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.switch import TuyaSwitchDefinition
from tuya_device_handlers.registry import QuirksRegistry

from . import create_device
from .const import DEVICE_FIXTURES


def _get_entity_details(
    definition: TuyaSwitchDefinition, device: CustomerDevice
) -> dict[str, Any]:
    """Generate snapshot details."""
    entity_details: dict[str, Any] = {}

    if (wrapper := definition.switch_wrapper) is not None:
        entity_details["state"] = wrapper.read_device_status(device)

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
    if quirk is None or quirk.switch_quirks is None:
        return
    for entity_quirk in quirk.switch_quirks:
        definition = entity_quirk.definition_fn(device)
        if definition is None:
            continue

        assert dataclasses.asdict(entity_quirk) == snapshot(
            name=f"{entity_quirk.key}-definition",
            exclude=props("definition_fn"),
        )
        assert _get_entity_details(definition, device) == snapshot(
            name=f"{entity_quirk.key}-state"
        )
