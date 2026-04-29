"""Tests for the quirks registry."""

from unittest.mock import Mock

from tuya_sharing import CustomerDevice

from tuya_device_handlers.registry import QuirksRegistry


def test_singleton_preserves_state() -> None:
    """Test that re-instantiating QuirksRegistry does not wipe registered quirks."""
    reg = QuirksRegistry()

    # Register a quirk
    quirk = Mock()
    device = Mock(spec=CustomerDevice)
    device.product_id = "test_product_singleton"
    reg.register("test_product_singleton", quirk)

    # Second instantiation should return same instance with data intact
    reg2 = QuirksRegistry()
    assert reg2 is reg
    assert reg2.get_quirk_for_device(device) is quirk

    # Cleanup
    reg._quirks.pop("test_product_singleton", None)
