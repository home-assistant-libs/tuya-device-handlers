"""Tests for the quirks registry."""

import pathlib
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


def test_initialise_device_quirk_applies_registered_quirk() -> None:
    """initialise_device_quirk delegates to the matching quirk."""
    reg = QuirksRegistry()
    quirk = Mock()
    device = Mock(spec=CustomerDevice)
    device.product_id = "test_product_init"
    reg.register("test_product_init", quirk)

    reg.initialise_device_quirk(device)

    quirk.initialise_device.assert_called_once_with(device)


def test_initialise_device_quirk_no_match_is_noop() -> None:
    """initialise_device_quirk silently skips unknown product_ids."""
    reg = QuirksRegistry()
    device = Mock(spec=CustomerDevice)
    device.product_id = "unknown_product"

    reg.initialise_device_quirk(device)  # must not raise


def test_purge_custom_quirks_removes_quirks_under_root() -> None:
    """purge_custom_quirks drops quirks whose file lives under the given root."""
    reg = QuirksRegistry()

    custom_root = "/tmp/custom_quirks"
    custom_quirk = Mock()
    custom_quirk.quirk_file = pathlib.Path(f"{custom_root}/foo.py")
    builtin_quirk = Mock()
    builtin_quirk.quirk_file = pathlib.Path("/usr/lib/builtin/bar.py")

    reg.register("custom_product", custom_quirk)
    reg.register("builtin_product", builtin_quirk)

    reg.purge_custom_quirks(custom_root)

    assert "custom_product" not in reg._quirks
    assert reg._quirks.get("builtin_product") is builtin_quirk
