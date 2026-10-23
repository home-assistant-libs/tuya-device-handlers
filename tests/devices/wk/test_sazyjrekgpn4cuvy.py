"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.device_wrapper.common import DPCodeIntegerWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Battery percentage 5 (raw) should be reported as 100 %."""
    device = create_device("wk_sazyjrekgpn4cuvy.json")
    filled_quirks_registry.initialise_device_quirk(device)

    wrapper = DPCodeIntegerWrapper.find_dpcode(device, "battery_percentage")
    assert wrapper is not None
    assert wrapper.native_unit == ""
    assert wrapper.min_value == 0
    assert wrapper.max_value == 100
    assert wrapper.value_step == 20
    assert wrapper.read_device_status(device) == 100

    device.status["battery_percentage"] = 1
    assert wrapper.read_device_status(device) == 20
