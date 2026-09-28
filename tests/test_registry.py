"""Tests for the quirks registry."""

import pathlib
import sys
import threading
from unittest.mock import Mock

from tuya_sharing import CustomerDevice

from tuya_device_handlers.registry import QuirksRegistry


def test_singleton_preserves_state() -> None:
    """Re-instantiating QuirksRegistry preserves quirks."""
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
    """purge_custom_quirks drops quirks under the given root."""
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


def test_purge_custom_quirks_during_concurrent_registration() -> None:
    """purge_custom_quirks tolerates another thread registering quirks.

    Home Assistant sets up each config entry in its own executor job, so two
    threads can be inside register_tuya_quirks at the same time: one purging
    while the other is still executing custom quirk modules.
    """
    reg = QuirksRegistry()
    custom_root = "/tmp/custom_quirks_concurrent"

    # Give the purge a large dict to walk, so the iteration is long enough to
    # actually be preempted by the registering thread.
    for index in range(5000):
        builtin = Mock()
        builtin.quirk_file = pathlib.Path(f"/usr/lib/builtin/mod{index}.py")
        reg.register(f"builtin_{index}", builtin)

    stop = threading.Event()
    errors: list[Exception] = []

    def _churn() -> None:
        index = 0
        while not stop.is_set():
            quirk = Mock()
            quirk.quirk_file = pathlib.Path(f"{custom_root}/mod{index}.py")
            reg.register(f"concurrent_{index}", quirk)
            index += 1

    def _purge() -> None:
        try:
            for _ in range(5):
                reg.purge_custom_quirks(custom_root)
        except Exception as err:  # noqa: BLE001
            errors.append(err)

    churn_thread = threading.Thread(target=_churn)
    original_interval = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    churn_thread.start()
    try:
        _purge()
    finally:
        stop.set()
        churn_thread.join(timeout=5)
        sys.setswitchinterval(original_interval)

    assert not errors


def test_reloading_does_not_block_readers() -> None:
    """Readers never wait on a reload.

    Reads run on Home Assistant's event loop, while a reload executes
    arbitrary custom quirk modules off it -- so a reader that blocked on the
    reload would stall the loop for as long as that takes.
    """
    reg = QuirksRegistry()
    device = Mock(spec=CustomerDevice)
    device.product_id = "reloading_product"

    read_finished = threading.Event()

    def _read() -> None:
        reg.get_quirk_for_device(device)
        read_finished.set()

    reader = threading.Thread(target=_read)
    with reg.reloading():
        reader.start()
        assert read_finished.wait(timeout=5)

    reader.join(timeout=5)


def test_reloading_hides_the_purged_state_from_readers() -> None:
    """A reload is published as one swap, so no reader sees a partial purge."""
    reg = QuirksRegistry()
    custom_root = "/tmp/custom_quirks_atomic"

    device = Mock(spec=CustomerDevice)
    device.product_id = "atomic_product"

    before = Mock()
    before.quirk_file = pathlib.Path(f"{custom_root}/foo.py")
    reg.register("atomic_product", before)

    with reg.reloading():
        reg.purge_custom_quirks(custom_root)
        # Mid-reload the quirk is gone from the staging copy, but a reader
        # still sees the previous mapping rather than nothing.
        assert reg.get_quirk_for_device(device) is before

        after = Mock()
        after.quirk_file = pathlib.Path(f"{custom_root}/foo.py")
        reg.register("atomic_product", after)

    assert reg.get_quirk_for_device(device) is after


def test_reloading_is_reentrant() -> None:
    """Quirk modules register on the reloading thread, so the lock reenters."""
    reg = QuirksRegistry()
    quirk = Mock()
    quirk.quirk_file = pathlib.Path("/tmp/custom_quirks_reentrant/foo.py")

    with reg.reloading():
        reg.purge_custom_quirks("/tmp/custom_quirks_reentrant")
        reg.register("reentrant_product", quirk)

    assert reg._quirks["reentrant_product"] is quirk


def test_nested_reloading_publishes_once() -> None:
    """A nested reloading block neither re-snapshots nor publishes early."""
    reg = QuirksRegistry()
    device = Mock(spec=CustomerDevice)
    device.product_id = "nested_product"

    quirk = Mock()
    quirk.quirk_file = pathlib.Path("/tmp/custom_quirks_nested/foo.py")

    with reg.reloading():
        with reg.reloading():
            reg.register("nested_product", quirk)
        # The inner block must not have published on exit.
        assert reg.get_quirk_for_device(device) is None

    assert reg.get_quirk_for_device(device) is quirk
