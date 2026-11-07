"""Test device-level quirk initialisation."""

from unittest.mock import patch

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk rescales temperatures (reported in half degrees)."""
    device = create_device("wk_IAYz2WK1th0cMLmL.json")
    assert device.status["temp_set"] == 46
    assert device.status["upper_temp"] == 45

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        definition = get_default_definition(
            device, TuyaUnitOfTemperature.CELSIUS
        )
    current = definition.current_temperature_wrapper
    target = definition.set_temperature_wrapper
    assert current is not None
    assert target is not None
    # Advertised as whole degrees / tenths
    assert current.read_device_status(device) == 45
    assert target.read_device_status(device) == 4.6
    assert (target.min_value, target.max_value, target.value_step) == (
        1,
        7,
        0.5,
    )

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    current = definition.current_temperature_wrapper
    target = definition.set_temperature_wrapper
    assert current is not None
    assert target is not None
    assert current.read_device_status(device) == 22.5
    assert target.read_device_status(device) == 23
    assert (target.min_value, target.max_value, target.value_step) == (
        5,
        35,
        0.5,
    )
    assert target.get_update_commands(device, 21.5) == [
        {"code": "temp_set", "value": 43}
    ]
