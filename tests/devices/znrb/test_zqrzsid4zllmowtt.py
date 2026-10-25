"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing `make_hot` mode value."""
    device = create_device("znrb_zqrzsid4zllmowtt.json")
    assert device.status["mode"] == "make_hot"

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "mode", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["auto"]
    assert wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "mode", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["auto", "make_hot"]
    assert wrapper.read_device_status(device) == "make_hot"
