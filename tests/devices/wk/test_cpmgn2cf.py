"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk."""
    device = create_device("wk_cpmgn2cf.json")

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == []
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == [
        "holiday",
        "auto",
        "manual",
        "eco",
    ]

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    assert definition.hvac_mode_wrapper is not None
    assert definition.hvac_mode_wrapper.options == []
    assert definition.preset_wrapper is not None
    assert definition.preset_wrapper.options == [
        "holiday",
        "auto",
        "manual",
        "comfort",
        "eco",
        "BOOST",
        "temp_auto",
    ]
