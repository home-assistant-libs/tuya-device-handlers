"""Tests for quirk registration."""

import logging
import pathlib
from unittest.mock import Mock

import pytest
from tuya_sharing import CustomerDevice

from tuya_device_handlers.devices import register_tuya_quirks
from tuya_device_handlers.registry import QuirksRegistry

_CUSTOM_QUIRK = '''\
"""Custom quirk used by the test suite."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="{product_id}")
    .add_dpid_integer(
        dpid=101,
        dpcode="{dpcode}",
        dpmode=DPMode.READ,
        unit="C",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
'''


def _write_quirk(
    root: pathlib.Path, name: str, product_id: str, dpcode: str
) -> None:
    """Write a custom quirk module into `root`."""
    (root / f"{name}.py").write_text(
        _CUSTOM_QUIRK.format(product_id=product_id, dpcode=dpcode)
    )


def test_custom_quirks_are_registered(
    filled_quirks_registry: QuirksRegistry, tmp_path: pathlib.Path
) -> None:
    """Custom quirks are loaded from the custom path."""
    _write_quirk(tmp_path, "custom_one", "custom_product_one", "ext_temp")

    register_tuya_quirks(str(tmp_path))

    quirk = filled_quirks_registry._quirks["custom_product_one"]
    assert quirk.quirk_file.is_relative_to(tmp_path)


def test_custom_quirks_are_reloaded(
    filled_quirks_registry: QuirksRegistry, tmp_path: pathlib.Path
) -> None:
    """A second call purges the previous custom quirks and reloads them.

    Built-in quirks must survive the purge, and a custom quirk whose file has
    been deleted must not.
    """
    _write_quirk(tmp_path, "custom_one", "custom_product_one", "ext_temp")
    _write_quirk(tmp_path, "custom_two", "custom_product_two", "ext_hum")
    register_tuya_quirks(str(tmp_path))
    assert "custom_product_one" in filled_quirks_registry._quirks

    # Drop one quirk file and change the other.
    (tmp_path / "custom_one.py").unlink()
    _write_quirk(tmp_path, "custom_two", "custom_product_two", "changed_code")

    register_tuya_quirks(str(tmp_path))

    assert "custom_product_one" not in filled_quirks_registry._quirks
    device = Mock(spec=CustomerDevice)
    device.product_id = "custom_product_two"
    device.category = "wk"
    device.function = {}
    device.status_range = {}
    device.local_strategy = {}
    device.support_local = True
    filled_quirks_registry.initialise_device_quirk(device)
    assert "changed_code" in device.status_range
    # Built-in quirks are untouched by the purge.
    assert "m7kacaxrxbxeegfs" in filled_quirks_registry._quirks


def test_broken_custom_quirk_is_logged_and_skipped(
    filled_quirks_registry: QuirksRegistry, tmp_path: pathlib.Path
) -> None:
    """One bad custom quirk does not stop the others from loading."""
    (tmp_path / "broken.py").write_text("raise RuntimeError('boom')\n")
    _write_quirk(tmp_path, "custom_one", "custom_product_one", "ext_temp")

    register_tuya_quirks(str(tmp_path))

    assert "custom_product_one" in filled_quirks_registry._quirks


@pytest.mark.usefixtures("filled_quirks_registry")
def test_empty_custom_quirks_path_is_quiet(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An empty custom path loads nothing and logs no "contribute" warning."""
    with caplog.at_level(logging.WARNING):
        register_tuya_quirks(str(tmp_path))

    assert "contribute" not in caplog.text


def test_custom_quirk_shadowing_a_builtin_is_undone_on_removal(
    filled_quirks_registry: QuirksRegistry, tmp_path: pathlib.Path
) -> None:
    """Deleting a custom quirk uncovers the built-in it was shadowing.

    Quirks register as an import side effect, so a built-in cannot register
    twice in one process. Without a cached snapshot, purging the custom
    quirk would drop support for the device until the host restarts.
    """
    builtin_product = "m7kacaxrxbxeegfs"
    builtin = filled_quirks_registry._quirks[builtin_product]

    _write_quirk(tmp_path, "shadow", builtin_product, "shadowed_code")
    register_tuya_quirks(str(tmp_path))
    shadowing = filled_quirks_registry._quirks[builtin_product]
    assert shadowing is not builtin
    assert shadowing.quirk_file.is_relative_to(tmp_path)

    (tmp_path / "shadow.py").unlink()
    register_tuya_quirks(str(tmp_path))

    assert filled_quirks_registry._quirks[builtin_product] is builtin
