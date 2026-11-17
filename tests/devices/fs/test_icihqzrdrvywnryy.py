"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.fan import get_default_definition
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing `normal` and `temprature` mode values."""
    device = create_device("fs_icihqzrdrvywnryy.json")
    device.status["mode"] = "temprature"

    definition = get_default_definition(device)
    assert definition is not None
    assert definition.mode_wrapper is not None
    assert definition.mode_wrapper.options == ["sleep", "nature"]
    assert definition.mode_wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    definition = get_default_definition(device)
    assert definition is not None
    assert definition.mode_wrapper is not None
    assert definition.mode_wrapper.options == [
        "normal",
        "sleep",
        "nature",
        "temprature",
    ]
    assert definition.mode_wrapper.read_device_status(device) == "temprature"
