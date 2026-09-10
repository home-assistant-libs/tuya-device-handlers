"""Test device-level quirk initialisation for InverFlow pool pump."""

from tests import create_device
from tuya_device_handlers.registry import QuirksRegistry


def test_inverflow_pool_pump_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test that quirk adds missing control and telemetry datapoints."""
    device = create_device("hwsb_ircs2n82vgrozoew.json")

    assert "switch" not in device.function
    assert "mode" not in device.function

    filled_quirks_registry.initialise_device_quirk(device)

    assert "switch" in device.function
    assert "mode" in device.function
    assert "speed_set" in device.function
    assert "flow_rate" in device.status_range
    assert "add_ele" in device.status_range
