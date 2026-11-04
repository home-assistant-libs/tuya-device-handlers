"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds temp_current (reported in tenths of a degree)."""
    device = create_device("wk_lmtejj3f4kafi2k1.json")
    assert device.status["temp_current"] == 215

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    # DP 105 is not declared by the cloud
    assert definition.current_temperature_wrapper is None

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.current_temperature_wrapper is not None
    assert (
        definition.current_temperature_wrapper.read_device_status(device)
        == 21.5
    )
