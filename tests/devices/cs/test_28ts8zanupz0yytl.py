"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing `med` fan speed value."""
    device = create_device("cs_28ts8zanupz0yytl.json")
    assert device.status["fan_speed_enum"] == "med"

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "fan_speed_enum", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["low", "high"]
    assert wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "fan_speed_enum", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["low", "med", "high"]
    assert wrapper.read_device_status(device) == "med"
