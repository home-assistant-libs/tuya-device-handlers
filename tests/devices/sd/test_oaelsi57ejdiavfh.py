"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing `closed` cistern value."""
    device = create_device("sd_oaelsi57ejdiavfh.json")
    assert device.status["cistern"] == "closed"

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "cistern", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["low", "middle", "high"]
    assert wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "cistern", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["closed", "low", "middle", "high"]
    assert wrapper.read_device_status(device) == "closed"
