"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk adds missing `Random_Clean` status value."""
    device = create_device("sd_txitlmevigna7hyc.json")
    device.status["status"] = "Random_Clean"

    wrapper = DPCodeEnumWrapper.find_dpcode(device, "status")
    assert wrapper is not None
    assert "Random_Clean" not in wrapper.options
    assert wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    wrapper = DPCodeEnumWrapper.find_dpcode(device, "status")
    assert wrapper is not None
    assert "Random_Clean" in wrapper.options
    assert wrapper.read_device_status(device) == "Random_Clean"
