"""Test utils"""

import dataclasses
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.climate import TuyaClimateDefinition
from tuya_device_handlers.device_wrapper.base import DeviceWrapper
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry

from . import create_device
from .const import DEVICE_FIXTURES


def _get_entity_details(
    definition: TuyaClimateDefinition, device: CustomerDevice
) -> dict[str, Any]:
    """Generate snapshot details."""
    entity_details: dict[str, Any] = {
        "temperature_unit": definition.temperature_unit
    }

    wrapper: DeviceWrapper[Any] | None
    if (wrapper := definition.current_humidity_wrapper) is not None:
        entity_details["current_humidity"] = wrapper.read_device_status(device)
    if (wrapper := definition.current_temperature_wrapper) is not None:
        entity_details["current_temperature"] = wrapper.read_device_status(
            device
        )
    if (wrapper := definition.target_humidity_wrapper) is not None:
        entity_details["target_humidity"] = wrapper.read_device_status(device)
    if (wrapper := definition.set_temperature_wrapper) is not None:
        entity_details["target_temperature"] = wrapper.read_device_status(
            device
        )
    if (wrapper := definition.fan_mode_wrapper) is not None:
        entity_details["fan_mode"] = wrapper.read_device_status(device)
        entity_details["fan_mode_options"] = wrapper.options
    if (wrapper := definition.hvac_mode_wrapper) is not None:
        entity_details["hvac_mode"] = wrapper.read_device_status(device)
        entity_details["hvac_mode_options"] = wrapper.options
    if (wrapper := definition.preset_wrapper) is not None:
        entity_details["preset"] = wrapper.read_device_status(device)
        entity_details["preset_options"] = wrapper.options
    if (wrapper := definition.swing_wrapper) is not None:
        entity_details["swing"] = wrapper.read_device_status(device)
        entity_details["swing_options"] = wrapper.options

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
