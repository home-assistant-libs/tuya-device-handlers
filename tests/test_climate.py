"""Test utils"""

import dataclasses
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from tuya_device_handlers.definition.climate import TuyaClimateDefinition
from tuya_device_handlers.device_wrapper.common import DPCodeIntegerWrapper
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry

from . import create_device
from .const import DEVICE_FIXTURES


def _get_entity_details(
    definition: TuyaClimateDefinition, device: CustomerDevice
) -> dict[str, Any]:
    """Generate snapshot details."""
    entity_details: dict[str, Any] = {
        "target_temp": None,
        "target_temp_dp_code": None,
        "target_temp_min": None,
        "target_temp_max": None,
        "target_temp_step": None,
        "current_temp": None,
        "current_temp_dp_code": None,
    }

    if (
        int_definition := definition.target_temperature_dp_type(device)
    ) is not None and isinstance(int_definition, DPCodeIntegerWrapper):
        entity_details["target_temp_dp_code"] = int_definition.dpcode
        entity_details["target_temp_min"] = int_definition.min_value
        entity_details["target_temp_max"] = int_definition.max_value
        entity_details["target_temp_step"] = int_definition.value_step
        if (status := device.status.get(int_definition.dpcode)) is not None:
            entity_details["target_temp"] = (
                int_definition.type_information.scale_value(status)
            )

    if (
        int_definition := definition.current_temperature_dp_type(device)
    ) is not None and isinstance(int_definition, DPCodeIntegerWrapper):
        entity_details["current_temp_dp_code"] = int_definition.dpcode
        if (status := device.status.get(int_definition.dpcode)) is not None:
            entity_details["current_temp"] = (
                int_definition.type_information.scale_value(status)
            )

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
    if quirk is None or quirk.climate_quirks is None:
        return
    for entity_quirk in quirk.climate_quirks:
        definition = entity_quirk.definition_fn(
            device, TuyaUnitOfTemperature.CELSIUS
        )
        if definition is None:
            continue

        assert dataclasses.asdict(entity_quirk) == snapshot(
            name=f"{entity_quirk.key}-definition",
            exclude=props("definition_fn"),
        )
        assert _get_entity_details(definition, device) == snapshot(
            name=f"{entity_quirk.key}-state"
        )
