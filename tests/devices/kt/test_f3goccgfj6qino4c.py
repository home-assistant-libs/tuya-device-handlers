"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing `wind` mode and `strong` fan speed."""
    device = create_device("kt_f3goccgfj6qino4c.json")

    mode_wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "mode", prefer_function=True
    )
    assert mode_wrapper is not None
    assert "wind" not in mode_wrapper.options

    fan_wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "fan_speed_enum", prefer_function=True
    )
    assert fan_wrapper is not None
    assert "strong" not in fan_wrapper.options

    filled_quirks_registry.initialise_device_quirk(device)

    mode_wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "mode", prefer_function=True
    )
    assert mode_wrapper is not None
    assert "wind" in mode_wrapper.options

    fan_wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "fan_speed_enum", prefer_function=True
    )
    assert fan_wrapper is not None
    assert "strong" in fan_wrapper.options
